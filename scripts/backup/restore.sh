#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

BACKUP_DIR="${BACKUP_DIR:-/backups}"
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-}"
DB_USER="${POSTGRES_USER:-}"
DB_PASSWORD="${POSTGRES_PASSWORD:-}"
ADMIN_DB="${POSTGRES_ADMIN_DB:-postgres}"
CHROMA_TARGET_DIR="${CHROMA_TARGET_DIR:-/data/chroma_db}"
CHROMA_PREFIX="${CHROMA_PREFIX:-chroma}"
BACKUP_PREFIX="${BACKUP_PREFIX:-backup}"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

die() {
  log "ERROR: $*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

verify_config() {
  [ -n "$DB_NAME" ] || die 'POSTGRES_DB is required'
  [ -n "$DB_USER" ] || die 'POSTGRES_USER is required'
  [ -n "$DB_PASSWORD" ] || die 'POSTGRES_PASSWORD is required'
}

wait_for_db() {
  local retries="${DB_HEALTH_RETRIES:-30}"
  local sleep_seconds="${DB_HEALTH_SLEEP_SECONDS:-2}"
  local attempt=1

  export PGPASSWORD="$DB_PASSWORD"
  while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$ADMIN_DB" >/dev/null 2>&1; do
    if [ "$attempt" -ge "$retries" ]; then
      die "Database ${DB_HOST}:${DB_PORT}/${ADMIN_DB} did not become ready after ${retries} attempts"
    fi
    log "Waiting for database ${DB_HOST}:${DB_PORT}/${ADMIN_DB} (attempt ${attempt}/${retries})"
    attempt=$((attempt + 1))
    sleep "$sleep_seconds"
  done
}

verify_checksum_if_present() {
  local file="$1"
  local checksum_file="${file}.sha256"

  if [ -f "$checksum_file" ]; then
    sha256sum -c "$checksum_file" >/dev/null || die "Checksum verification failed: $checksum_file"
    log "Checksum OK: $checksum_file"
  else
    log "Checksum file not found, skipping checksum verification: $checksum_file"
  fi
}

verify_dump_file() {
  local dump_file="$1"
  [ -s "$dump_file" ] || die "Backup file is empty: $dump_file"
  pg_restore -l "$dump_file" >/dev/null || die 'Backup validation failed before restore'
}

select_latest_backup() {
  find "$BACKUP_DIR" -maxdepth 1 -type f -name "${BACKUP_PREFIX}_*.dump" -printf '%T@ %p\n' \
    | sort -rn \
    | awk 'NR==1 {print $2}'
}

confirm() {
  local prompt="$1"
  local reply
  printf '%s ' "$prompt"
  read -r reply
  [ "$reply" = 'yes' ]
}

terminate_db_connections() {
  export PGPASSWORD="$DB_PASSWORD"
  psql -v ON_ERROR_STOP=1 -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$ADMIN_DB" <<SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '${DB_NAME}'
  AND pid <> pg_backend_pid();
SQL
}

restore_postgres() {
  local dump_file="$1"
  export PGPASSWORD="$DB_PASSWORD"

  terminate_db_connections

  pg_restore \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --clean \
    --if-exists \
    --no-owner \
    --no-acl \
    --exit-on-error \
    --single-transaction \
    "$dump_file" || die 'PostgreSQL restore failed'
}

restore_chroma_if_available() {
  local dump_file="$1"
  local timestamp
  local chroma_file

  timestamp="$(basename "$dump_file" | sed -E "s/^${BACKUP_PREFIX}_(.*)\\.dump$/\\1/")"
  chroma_file="$BACKUP_DIR/${CHROMA_PREFIX}_${timestamp}.tar.gz"

  if [ ! -f "$chroma_file" ]; then
    log "No matching Chroma backup found for timestamp: $timestamp"
    return 0
  fi

  verify_checksum_if_present "$chroma_file"

  echo
  log "Matching Chroma backup found: $chroma_file"
  if confirm "Restore Chroma too? Type 'yes' to continue:"; then
    mkdir -p "$(dirname "$CHROMA_TARGET_DIR")"
    rm -rf "$CHROMA_TARGET_DIR"
    tar -xzf "$chroma_file" -C "$(dirname "$CHROMA_TARGET_DIR")"
    log 'Chroma restored.'
  else
    log 'Skipped Chroma restore.'
  fi
}

main() {
  require_command pg_restore
  require_command pg_isready
  require_command psql
  require_command sha256sum
  require_command find
  require_command awk
  require_command sort
  require_command tar
  verify_config
  wait_for_db

  local dump_file="${1:-}"
  if [ -z "$dump_file" ]; then
    echo 'Available backups:'
    find "$BACKUP_DIR" -maxdepth 1 -type f -name "${BACKUP_PREFIX}_*.dump" -print | sort -r || true
    echo

    dump_file="$(select_latest_backup)"
    [ -n "$dump_file" ] || die "No backup files found in $BACKUP_DIR"
    log "Selected most recent backup: $dump_file"
  fi

  [ -f "$dump_file" ] || die "Backup file not found: $dump_file"

  verify_checksum_if_present "$dump_file"
  verify_dump_file "$dump_file"

  echo
  log "WARNING: This will overwrite the current database '$DB_NAME'."
  if ! confirm "Type 'yes' to continue:"; then
    log 'Restore cancelled.'
    exit 0
  fi

  log "Restoring PostgreSQL from: $dump_file"
  restore_postgres "$dump_file"
  log 'PostgreSQL restored successfully.'

  restore_chroma_if_available "$dump_file"

  log 'Restore complete.'
}

main "$@"
