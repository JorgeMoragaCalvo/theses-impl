#!/usr/bin/env bash
set -Eeuo pipefail

BACKUP_SCHEDULE="${BACKUP_SCHEDULE:-0 2 * * *}"
CRONTAB_FILE="/tmp/backup-crontab"
BACKUP_COMMAND="${BACKUP_COMMAND:-/app/scripts/backup.sh}"
RUN_ON_STARTUP="${BACKUP_RUN_ON_STARTUP:-false}"
RESTORE_SMOKE_TEST_COMMAND="${RESTORE_SMOKE_TEST_COMMAND:-/app/scripts/restore-smoke-test.sh}"
RESTORE_SMOKE_TEST_SCHEDULE="${RESTORE_SMOKE_TEST_SCHEDULE:-}"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

log "Backup scheduler starting. Schedule: ${BACKUP_SCHEDULE}"

if [ "$RUN_ON_STARTUP" = 'true' ]; then
  log 'Running initial backup before scheduler starts'
  "$BACKUP_COMMAND"
fi

printf '%s %s\n' "$BACKUP_SCHEDULE" "$BACKUP_COMMAND" > "$CRONTAB_FILE"
if [ -n "$RESTORE_SMOKE_TEST_SCHEDULE" ]; then
  printf '%s %s\n' "$RESTORE_SMOKE_TEST_SCHEDULE" "$RESTORE_SMOKE_TEST_COMMAND" >> "$CRONTAB_FILE"
  log "Restore smoke test scheduled: ${RESTORE_SMOKE_TEST_SCHEDULE}"
fi
exec supercronic "$CRONTAB_FILE"
