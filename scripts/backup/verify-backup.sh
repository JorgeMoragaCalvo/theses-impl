#!/usr/bin/env bash
set -Eeuo pipefail

umask 077

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-}"
DB_USER="${POSTGRES_USER:-}"
DB_PASSWORD="${POSTGRES_PASSWORD:-}"

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

verify_dump_contents() {
  local dump_file="$1"
  pg_restore -l "$dump_file"
}

main() {
  require_command pg_restore
  require_command sha256sum
  require_command stat

  local dump_file="${1:-}"
  [ -n "$dump_file" ] || die "Usage: $0 <backup-file.dump>"
  [ -f "$dump_file" ] || die "File not found: $dump_file"

  local file_size
  file_size="$(file_size_bytes "$dump_file")"
  [ "$file_size" -gt 0 ] || die "File is empty: $dump_file"

  log "File size: $file_size bytes"
  verify_checksum_if_present "$dump_file"

  echo
  echo 'Backup contents:'
  echo '================'
  verify_dump_contents "$dump_file" || die 'pg_restore verification failed'
  echo
  log 'Verification passed.'
}

main "$@"
