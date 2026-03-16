#!/usr/bin/env bash
set -euo pipefail

umask 077

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
ENV_FILE="$PROJECT_ROOT/.env"

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

load_env_file() {
  local env_file="$1"
  [ -f "$env_file" ] || die ".env file not found at $env_file"

  while IFS= read -r line || [ -n "$line" ]; do
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"

    [ -z "$line" ] && continue
    case "$line" in
      \#*) continue ;;
    esac

    case "$line" in
      *=*)
        local key="${line%%=*}"
        local value="${line#*=}"

        key="${key%"${key##*[![:space:]]}"}"
        value="${value#"${value%%[![:space:]]*}"}"

        if [[ ! "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
          die "Invalid variable name in .env: $key"
        fi

        if [[ "$value" =~ ^\".*\"$ ]]; then
          value="${value:1:${#value}-2}"
        elif [[ "$value" =~ ^\'.*\'$ ]]; then
          value="${value:1:${#value}-2}"
        fi

        export "$key=$value"
        ;;
      *)
        die "Invalid line in .env: $line"
        ;;
    esac
  done < "$env_file"
}

verify_required_env() {
  : "${POSTGRES_USER:?POSTGRES_USER not set in .env}"
  : "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD not set in .env}"
  : "${POSTGRES_DB:?POSTGRES_DB not set in .env}"
}

ensure_db_running() {
  if ! docker compose -f "$COMPOSE_FILE" ps db --format '{{.State}}' 2>/dev/null | grep -qi '^running$'; then
    die "db container is not running. Start it with: docker compose up -d db"
  fi
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

  docker compose -f "$COMPOSE_FILE" exec -T db \
    sh -lc 'cat > /tmp/restore_verify.dump && pg_restore -l /tmp/restore_verify.dump >/dev/null && rm -f /tmp/restore_verify.dump' \
    < "$dump_file" || die "Backup validation failed before restore"
}

select_latest_backup() {
  find "$BACKUP_DIR" -maxdepth 1 -type f -name 'backup_*.dump' -printf '%T@ %p\n' \
    | sort -rn \
    | awk 'NR==1 {print $2}'
}

confirm() {
  local prompt="$1"
  local reply

  printf '%s ' "$prompt"
  read -r reply
  [ "$reply" = "yes" ]
}

restore_postgres() {
  local dump_file="$1"
  local restore_log
  restore_log="$(mktemp)"

  if ! docker compose -f "$COMPOSE_FILE" exec -T db \
      env PGPASSWORD="$POSTGRES_PASSWORD" \
      sh -lc '
        cat > /tmp/restore.dump &&
        pg_restore \
          -U "$POSTGRES_USER" \
          -d "$POSTGRES_DB" \
          --clean --if-exists --no-owner --no-acl --exit-on-error \
          /tmp/restore.dump
        status=$?
        rm -f /tmp/restore.dump
        exit $status
      ' >"$restore_log" 2>&1 < "$dump_file"; then
    cat "$restore_log" >&2
    rm -f "$restore_log"
    die "PostgreSQL restore failed"
  fi

  cat "$restore_log"
  rm -f "$restore_log"
}

restore_chroma_if_available() {
  local dump_file="$1"
  local timestamp
  local chroma_file

  timestamp="$(basename "$dump_file" | sed -E 's/^backup_(.*)\.dump$/\1/')"
  chroma_file="$BACKUP_DIR/chroma_${timestamp}.tar.gz"

  if [ ! -f "$chroma_file" ]; then
    log "No matching ChromaDB backup found for timestamp: $timestamp"
    return 0
  fi

  verify_checksum_if_present "$chroma_file"

  echo
  log "Matching ChromaDB backup found: $chroma_file"
  if confirm "Restore ChromaDB too? Type 'yes' to continue:"; then
    rm -rf "$PROJECT_ROOT/chroma_db"
    tar -xzf "$chroma_file" -C "$PROJECT_ROOT"
    log "ChromaDB restored."
  else
    log "Skipped ChromaDB restore."
  fi
}

require_command docker
require_command sha256sum
require_command find
require_command awk
require_command sort
require_command mktemp
require_command tar

load_env_file "$ENV_FILE"
verify_required_env
ensure_db_running

DUMP_FILE="${1:-}"

if [ -z "$DUMP_FILE" ]; then
  echo "Available backups:"
  find "$BACKUP_DIR" -maxdepth 1 -type f -name 'backup_*.dump' -print | sort -r || true
  echo

  DUMP_FILE="$(select_latest_backup)"
  [ -n "$DUMP_FILE" ] || die "No backup files found in $BACKUP_DIR"
  log "Selected most recent backup: $DUMP_FILE"
fi

[ -f "$DUMP_FILE" ] || die "Backup file not found: $DUMP_FILE"

verify_checksum_if_present "$DUMP_FILE"
verify_dump_file "$DUMP_FILE"

echo
log "WARNING: This will overwrite the current database '$POSTGRES_DB'."
if ! confirm "Type 'yes' to continue:"; then
  log "Restore cancelled."
  exit 0
fi

log "Restoring PostgreSQL from: $DUMP_FILE"
restore_postgres "$DUMP_FILE"
log "PostgreSQL restored successfully."

restore_chroma_if_available "$DUMP_FILE"

log "Restore complete."
