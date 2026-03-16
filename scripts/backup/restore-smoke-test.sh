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
BACKUP_PREFIX="${BACKUP_PREFIX:-backup}"
SMOKE_DB_PREFIX="${RESTORE_SMOKE_DB_PREFIX:-restore_smoke}"
SMOKE_KEEP_DB="${RESTORE_SMOKE_KEEP_DB:-false}"
SMOKE_TIMEOUT_SECONDS="${RESTORE_SMOKE_TIMEOUT_SECONDS:-600}"

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
  [[ "$SMOKE_TIMEOUT_SECONDS" =~ ^[0-9]+$ ]] || die 'RESTORE_SMOKE_TIMEOUT_SECONDS must be an integer'
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
  pg_restore -l "$dump_file" >/dev/null || die 'Backup validation failed before smoke test'
}

select_latest_backup() {
  find "$BACKUP_DIR" -maxdepth 1 -type f -name "${BACKUP_PREFIX}_*.dump" -printf '%T@ %p\n' \
    | sort -rn \
    | awk 'NR==1 {print $2}'
}

drop_database_if_exists() {
  local db_name="$1"
  export PGPASSWORD="$DB_PASSWORD"
  psql -v ON_ERROR_STOP=1 -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$ADMIN_DB" <<SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '${db_name}'
  AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS "${db_name}";
SQL
}

create_database() {
  local db_name="$1"
  export PGPASSWORD="$DB_PASSWORD"
  psql -v ON_ERROR_STOP=1 -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$ADMIN_DB" \
    -c "CREATE DATABASE \"${db_name}\";"
}

restore_into_database() {
  local dump_file="$1"
  local db_name="$2"
  export PGPASSWORD="$DB_PASSWORD"

  timeout "$SMOKE_TIMEOUT_SECONDS" pg_restore \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$db_name" \
    --no-owner \
    --no-acl \
    --exit-on-error \
    --single-transaction \
    "$dump_file" || die 'Smoke restore failed'
}

run_smoke_queries() {
  local db_name="$1"
  export PGPASSWORD="$DB_PASSWORD"

  psql -v ON_ERROR_STOP=1 -At -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$db_name" <<'SQL'
SELECT current_database();
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema');
SQL
}

main() {
  require_command pg_restore
  require_command pg_isready
  require_command psql
  require_command sha256sum
  require_command find
  require_command awk
  require_command sort
  require_command timeout
  verify_config
  wait_for_db

  local dump_file="${1:-}"
  if [ -z "$dump_file" ]; then
    dump_file="$(select_latest_backup)"
    [ -n "$dump_file" ] || die "No backup files found in $BACKUP_DIR"
    log "Selected most recent backup: $dump_file"
  fi

  [ -f "$dump_file" ] || die "Backup file not found: $dump_file"
  verify_checksum_if_present "$dump_file"
  verify_dump_file "$dump_file"

  local smoke_db="${SMOKE_DB_PREFIX}_$(date -u +%Y%m%d_%H%M%S)"
  trap 'if [ "${SMOKE_KEEP_DB}" != "true" ]; then drop_database_if_exists "$smoke_db" >/dev/null 2>&1 || true; fi' EXIT

  log "Creating temporary database: $smoke_db"
  create_database "$smoke_db"

  log "Restoring backup into temporary database"
  restore_into_database "$dump_file" "$smoke_db"

  log 'Running smoke queries'
  run_smoke_queries "$smoke_db"

  if [ "$SMOKE_KEEP_DB" = 'true' ]; then
    log "Smoke-test database preserved: $smoke_db"
  else
    drop_database_if_exists "$smoke_db"
    trap - EXIT
    log 'Smoke-test database dropped successfully'
  fi

  log 'Restore smoke test passed.'
}

main "$@"
