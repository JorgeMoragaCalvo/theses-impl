FROM postgres:16-alpine

ARG SUPERCRONIC_VERSION=v0.2.33

RUN apk add --no-cache bash coreutils findutils gawk tar gzip tzdata wget ca-certificates \
    && wget -O /usr/local/bin/supercronic \
       "https://github.com/aptible/supercronic/releases/download/${SUPERCRONIC_VERSION}/supercronic-linux-amd64" \
    && chmod +x /usr/local/bin/supercronic \
    && addgroup -S backup \
    && adduser -S -G backup -h /home/backup backup

WORKDIR /app

COPY scripts/backup/backup.sh scripts/backup/restore.sh scripts/backup/verify-backup.sh scripts/backup/restore-smoke-test.sh ./scripts/
COPY scripts/backup/entrypoint.sh ./entrypoint.sh

RUN chmod +x /app/scripts/*.sh /app/entrypoint.sh \
    && mkdir -p /backups /var/run/backup /data \
    && chown -R backup:backup /app /backups /var/run/backup /data

HEALTHCHECK --interval=60s --timeout=5s --start-period=20s --retries=3 \
  CMD test -f /var/run/backup/last-success.timestamp \
   && test $(( $(date -u +%s) - $(cat /var/run/backup/last-success.timestamp) )) -lt ${BACKUP_MAX_AGE_SECONDS:-172800}

USER backup

ENTRYPOINT ["/app/entrypoint.sh"]
