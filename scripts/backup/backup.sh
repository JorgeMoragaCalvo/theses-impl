#!/usr/bin/env bash
set -euo pipefail

umask 077

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
ENV_FILE="$PROJECT_ROOT/.env"
LOCK_DIR="$BACKUP_DIR/.backup.lock"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

die() {
  log "ERROR: $*" >&2
  exit 1
}

cleanup() {
  rm -rf "$LOCK_DIR"
}
trap cleanup EXIT

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

verify_dump_file() {
  local dump_file="$1"

  [ -s "$dump_file" ] || die "Backup file is empty: $dump_file"

  docker compose -f "$COMPOSE_FILE" exec -T db \
    sh -lc 'cat > /tmp/verify.dump && pg_restore -l /tmp/verify.dump >/dev/null && rm -f /tmp/verify.dump' \
    < "$dump_file" || die "Backup verification failed — dump may be corrupted"
}

write_checksum() {
  local file="$1"
  sha256sum "$file" > "${file}.sha256"
}

rotate_old_backups() {
  local prefix="$1"
  local extension="$2"
  local retention="${BACKUP_RETENTION:-7}"

  [[ "$retention" =~ ^[0-9]+$ ]] || die "BACKUP_RETENTION must be an integer"

  mapfile -t files < <(find "$BACKUP_DIR" -maxdepth 1 -type f -name "${prefix}_*.${extension}" -printf '%T@ %p\n' | sort -rn | awk '{print $2}')

  if [ "${#files[@]}" -le "$retention" ]; then
    return 0
  fi

  for file in "${files[@]:$retention}"; do
    rm -f -- "$file" "${file}.sha256"
  done

  log "Rotated old ${prefix} backups (kept last $retention)"
}

require_command docker
require_command sha256sum
require_command find
require_command awk
require_command sort

mkdir -p "$BACKUP_DIR"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  die "Another backup process appears to be running"
fi

load_env_file "$ENV_FILE"
verify_required_env
ensure_db_running

DUMP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.dump"
CHROMA_SOURCE="$PROJECT_ROOT/chroma_db"

log "Starting PostgreSQL backup..."

docker compose -f "$COMPOSE_FILE" exec -T db \
  env PGPASSWORD="$POSTGRES_PASSWORD" \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc --no-owner --no-acl \
  > "$DUMP_FILE" || {
    rm -f "$DUMP_FILE"
    die "pg_dump failed"
  }

verify_dump_file "$DUMP_FILE"
write_checksum "$DUMP_FILE"
log "PostgreSQL backup verified: $DUMP_FILE"

if [ -d "$CHROMA_SOURCE" ]; then
  CHROMA_FILE="$BACKUP_DIR/chroma_${TIMESTAMP}.tar.gz"
  tar -czf "$CHROMA_FILE" -C "$PROJECT_ROOT" chroma_db
  write_checksum "$CHROMA_FILE"
  log "ChromaDB backup created: $CHROMA_FILE"
fi

rotate_old_backups "backup" "dump"
rotate_old_backups "chroma" "tar.gz"

log "Backup complete. Retained last ${BACKUP_RETENTION:-7} backups."
