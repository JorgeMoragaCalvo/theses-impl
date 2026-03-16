#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RUNTIME_DIR="${RUNTIME_DIR:-/var/run/backup}"
LOCK_DIR="${RUNTIME_DIR}/lock"
LAST_SUCCESS_FILE="${RUNTIME_DIR}/last-success.timestamp"
LAST_FAILURE_FILE="${RUNTIME_DIR}/last-failure.timestamp"
LAST_RESULT_FILE="${RUNTIME_DIR}/last-result.txt"
TIMESTAMP="$(date -u +%Y%m%d_%H%M%S)"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-}"
DB_USER="${POSTGRES_USER:-}"
DB_PASSWORD="${POSTGRES_PASSWORD:-}"
CHROMA_SOURCE_DIR="${CHROMA_SOURCE_DIR:-/data/chroma_db}"
BACKUP_RETENTION_COUNT="${BACKUP_RETENTION_COUNT:-${BACKUP_RETENTION:-7}}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
BACKUP_PREFIX="${BACKUP_PREFIX:-backup}"
CHROMA_PREFIX="${CHROMA_PREFIX:-chroma}"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

die() {
  log "ERROR: $*" >&2
  printf 'failure\n' > "$LAST_RESULT_FILE" 2>/dev/null || true
  date -u +%s > "$LAST_FAILURE_FILE" 2>/dev/null || true
  exit 1
}

cleanup() {
  rm -rf "$LOCK_DIR"
}
trap cleanup EXIT

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

verify_config() {
  [ -n "$DB_NAME" ] || die 'POSTGRES_DB is required'
  [ -n "$DB_USER" ] || die 'POSTGRES_USER is required'
  [ -n "$DB_PASSWORD" ] || die 'POSTGRES_PASSWORD is required'
  [[ "$BACKUP_RETENTION_COUNT" =~ ^[0-9]+$ ]] || die 'BACKUP_RETENTION_COUNT must be an integer'
  [[ "$BACKUP_RETENTION_DAYS" =~ ^[0-9]+$ ]] || die 'BACKUP_RETENTION_DAYS must be an integer'
}

wait_for_db() {
  local retries="${DB_HEALTH_RETRIES:-30}"
  local sleep_seconds="${DB_HEALTH_SLEEP_SECONDS:-2}"
  local attempt=1

  export PGPASSWORD="$DB_PASSWORD"
  while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; do
    if [ "$attempt" -ge "$retries" ]; then
      die "Database ${DB_HOST}:${DB_PORT}/${DB_NAME} did not become ready after ${retries} attempts"
    fi
    log "Waiting for database ${DB_HOST}:${DB_PORT}/${DB_NAME} (attempt ${attempt}/${retries})"
    attempt=$((attempt + 1))
    sleep "$sleep_seconds"
  done
}

verify_dump_file() {
  local dump_file="$1"
  [ -s "$dump_file" ] || die "Backup file is empty: $dump_file"
  pg_restore -l "$dump_file" >/dev/null || die "Backup verification failed for $dump_file"
}

write_checksum() {
  local file="$1"
  sha256sum "$file" > "${file}.sha256"
}

rotate_old_backups_by_count() {
  local prefix="$1"
  local extension="$2"
  mapfile -t files < <(find "$BACKUP_DIR" -maxdepth 1 -type f -name "${prefix}_*.${extension}" -printf '%T@ %p\n' | sort -rn | awk '{print $2}')

  if [ "${#files[@]}" -le "$BACKUP_RETENTION_COUNT" ]; then
    return 0
  fi

  for file in "${files[@]:$BACKUP_RETENTION_COUNT}"; do
    rm -f -- "$file" "${file}.sha256"
  done

  log "Rotation by count completed for ${prefix} (kept ${BACKUP_RETENTION_COUNT})"
}

rotate_old_backups_by_age() {
  local prefix="$1"
  local extension="$2"

  if [ "$BACKUP_RETENTION_DAYS" -eq 0 ]; then
    return 0
  fi

  while IFS= read -r file; do
    [ -n "$file" ] || continue
    rm -f -- "$file" "${file}.sha256"
  done < <(find "$BACKUP_DIR" -maxdepth 1 -type f -name "${prefix}_*.${extension}" -mtime "+${BACKUP_RETENTION_DAYS}" -print)

  log "Rotation by age completed for ${prefix} (>${BACKUP_RETENTION_DAYS} days removed)"
}

backup_postgres() {
  local dump_file="$1"
  export PGPASSWORD="$DB_PASSWORD"

  log "Starting PostgreSQL backup to ${dump_file}"
  pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -Fc \
    --no-owner \
    --no-acl \
    --verbose \
    > "$dump_file" || {
      rm -f "$dump_file"
      die 'pg_dump failed'
    }

  verify_dump_file "$dump_file"
  write_checksum "$dump_file"
}

backup_chroma() {
  if [ -z "$CHROMA_SOURCE_DIR" ] || [ ! -d "$CHROMA_SOURCE_DIR" ]; then
    log 'Chroma backup skipped: source directory not configured or does not exist'
    return 0
  fi

  local chroma_file="$BACKUP_DIR/${CHROMA_PREFIX}_${TIMESTAMP}.tar.gz"
  local parent_dir
  parent_dir="$(dirname "$CHROMA_SOURCE_DIR")"
  local dir_name
  dir_name="$(basename "$CHROMA_SOURCE_DIR")"

  log "Starting Chroma backup from ${CHROMA_SOURCE_DIR}"
  tar -czf "$chroma_file" -C "$parent_dir" "$dir_name"
  [ -s "$chroma_file" ] || die "Chroma backup file is empty: $chroma_file"
  write_checksum "$chroma_file"
}

mark_success() {
  date -u +%s > "$LAST_SUCCESS_FILE"
  printf 'success\n' > "$LAST_RESULT_FILE"
}

main() {
  require_command pg_dump
  require_command pg_restore
  require_command pg_isready
  require_command sha256sum
  require_command find
  require_command awk
  require_command sort
  require_command tar

  mkdir -p "$BACKUP_DIR" "$RUNTIME_DIR"
  verify_config

  if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    die 'Another backup process appears to be running'
  fi

  wait_for_db

  local dump_file="$BACKUP_DIR/${BACKUP_PREFIX}_${TIMESTAMP}.dump"
  backup_postgres "$dump_file"
  backup_chroma

  rotate_old_backups_by_count "$BACKUP_PREFIX" 'dump'
  rotate_old_backups_by_count "$CHROMA_PREFIX" 'tar.gz'
  rotate_old_backups_by_age "$BACKUP_PREFIX" 'dump'
  rotate_old_backups_by_age "$CHROMA_PREFIX" 'tar.gz'

  mark_success
  log 'Backup completed successfully'
}

main "$@"
