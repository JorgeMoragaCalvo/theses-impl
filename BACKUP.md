# Database Backup & Restore

Automated PostgreSQL backup and restore scripts for the AI Tutoring System.

## Prerequisites

- Docker Compose stack running (`docker compose up -d`)
- `.env` file configured with `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- Bash shell (Linux/macOS terminal, or Git Bash on Windows)

## Quick Start

```bash
# Run a manual backup
bash scripts/backup/backup.sh

# Restore from the most recent backup
bash scripts/backup/restore.sh

# Restore from a specific backup
bash scripts/backup/restore.sh backups/backup_20260314_020000.dump

# Verify a backup file
bash scripts/backup/verify-backup.sh backups/backup_20260314_020000.dump
```

## Automated Scheduling

### Linux / macOS (cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2:00 AM
0 2 * * * /path/to/thesis-impl/scripts/backup/backup.sh >> /path/to/thesis-impl/backups/backup.log 2>&1
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task → name it "DB Backup"
3. Trigger: Daily at 2:00 AM
4. Action: Start a program
   - Program: `C:\Program Files\Git\bin\bash.exe`
   - Arguments: `E:/PyCharmProjects/thesis-impl/scripts/backup/backup.sh`
   - Start in: `E:\PyCharmProjects\thesis-impl`

## Configuration

| Variable           | Default | Description                                        |
|--------------------|---------|----------------------------------------------------|
| `BACKUP_RETENTION` | `7`     | Number of backups to keep (older ones are deleted) |

Set in your environment or `.env`:
```bash
export BACKUP_RETENTION=14  # Keep 2 weeks of backups
```

## What Gets Backed Up

- **PostgreSQL database** — all tables (students, conversations, messages, assessments, feedback, student_competencies, concept_hierarchy, review_sessions, activity_events) in compressed custom format (`.dump`)
- **ChromaDB vector store** — `chroma_db/` directory as `.tar.gz` archive

## What Does NOT Get Backed Up

- Application code (tracked in git)
- Environment variables (`.env` — back up separately and securely)
- SSL certificates (`nginx/ssl/`)
- Docker images (rebuilt from Dockerfiles)

## Troubleshooting

| Problem                            | Solution                                                                      |
|------------------------------------|-------------------------------------------------------------------------------|
| "db container is not running"      | Run `docker compose up -d db` and wait for healthy status                     |
| "POSTGRES_USER not set"            | Check that `.env` exists and has the required variables                       |
| Empty backup file                  | Check disk space and database connectivity                                    |
| pg_restore warnings during restore | Warnings about "does not exist" are normal when restoring to a fresh database |
| Permission denied on scripts       | Run `chmod +x scripts/backup/*.sh`                                            |
