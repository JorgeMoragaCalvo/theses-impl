#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

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

file_size_bytes() {
  stat -c%s "$1" 2>/dev/null || stat -f%z "$1" 2>/dev/null
}

ensure_db_running() {
  if ! docker compose -f "$COMPOSE_FILE" ps db --format '{{.State}}' 2>/dev/null | grep -qi '^running$'; then
    die "db container is not running (needed for pg_restore validation)"
  fi
}

verify_checksum_if_present() {
  local file="$1"
  local checksum_file="${file}.sha256"

  if [ -f "$checksum_file" ]; then
    sha256sum -c "$checksum_file" >/dev/null
    log "Checksum OK: $checksum_file"
  else
    log "Checksum file not found, skipping checksum verification: $checksum_file"
  fi
}

verify_dump_contents() {
  local dump_file="$1"

  docker compose -f "$COMPOSE_FILE" exec -T db \
    sh -lc 'cat > /tmp/verify.dump && pg_restore -l /tmp/verify.dump && rm -f /tmp/verify.dump' \
    < "$dump_file"
}

require_command docker
require_command sha256sum
require_command stat

DUMP_FILE="${1:-}"

[ -n "$DUMP_FILE" ] || die "Usage: $0 <backup-file.dump>"
[ -f "$DUMP_FILE" ] || die "File not found: $DUMP_FILE"

FILE_SIZE="$(file_size_bytes "$DUMP_FILE")"
[ "$FILE_SIZE" -gt 0 ] || die "File is empty: $DUMP_FILE"

log "File size: $FILE_SIZE bytes"
verify_checksum_if_present "$DUMP_FILE"
ensure_db_running

echo
echo "Backup contents:"
echo "================"

verify_dump_contents "$DUMP_FILE" || die "pg_restore verification failed"

echo
log "Verification passed."
