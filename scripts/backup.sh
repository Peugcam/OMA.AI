#!/bin/bash
# ============================================================================
# OMA.AI Automated Backup Script
# Backs up database, Redis, and video outputs
# ============================================================================

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="oma_backup_${TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

log_info "Starting backup: ${BACKUP_NAME}"

# ============================================================================
# 1. Backup PostgreSQL
# ============================================================================
log_info "Backing up PostgreSQL database..."

docker exec oma-postgres pg_dump -U oma oma_production | \
    gzip > "${BACKUP_DIR}/${BACKUP_NAME}/postgres.sql.gz"

if [ $? -eq 0 ]; then
    log_info "PostgreSQL backup completed"
else
    log_error "PostgreSQL backup failed!"
    exit 1
fi

# ============================================================================
# 2. Backup Redis
# ============================================================================
log_info "Backing up Redis data..."

docker exec oma-redis redis-cli BGSAVE
sleep 5

docker cp oma-redis:/data/dump.rdb \
    "${BACKUP_DIR}/${BACKUP_NAME}/redis.rdb"

if [ $? -eq 0 ]; then
    log_info "Redis backup completed"
else
    log_warn "Redis backup failed (non-critical)"
fi

# ============================================================================
# 3. Backup Video Outputs (last 7 days only)
# ============================================================================
log_info "Backing up recent video outputs..."

find ./outputs/videos -type f -mtime -7 -name "*.mp4" | \
    tar -czf "${BACKUP_DIR}/${BACKUP_NAME}/videos.tar.gz" -T -

if [ $? -eq 0 ]; then
    SIZE=$(du -sh "${BACKUP_DIR}/${BACKUP_NAME}/videos.tar.gz" | cut -f1)
    log_info "Video outputs backup completed (${SIZE})"
else
    log_warn "No videos to backup or backup failed"
fi

# ============================================================================
# 4. Backup Configuration Files
# ============================================================================
log_info "Backing up configuration files..."

tar -czf "${BACKUP_DIR}/${BACKUP_NAME}/config.tar.gz" \
    .env.example \
    docker-compose*.yml \
    monitoring/ \
    nginx/ \
    2>/dev/null

log_info "Configuration backup completed"

# ============================================================================
# 5. Create backup manifest
# ============================================================================
cat > "${BACKUP_DIR}/${BACKUP_NAME}/manifest.txt" <<EOF
OMA.AI Backup Manifest
======================
Timestamp: ${TIMESTAMP}
Date: $(date)
Hostname: $(hostname)

Contents:
- PostgreSQL database dump (compressed)
- Redis data snapshot
- Video outputs (last 7 days)
- Configuration files

Restoration:
1. Extract backup: tar -xzf oma_backup_*.tar.gz
2. Restore DB: gunzip -c postgres.sql.gz | docker exec -i oma-postgres psql -U oma oma_production
3. Restore Redis: docker cp redis.rdb oma-redis:/data/dump.rdb && docker restart oma-redis
4. Restore videos: tar -xzf videos.tar.gz -C ./outputs/videos
EOF

# ============================================================================
# 6. Compress entire backup
# ============================================================================
log_info "Compressing backup..."

cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"

BACKUP_SIZE=$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)
log_info "Backup compressed: ${BACKUP_SIZE}"

# ============================================================================
# 7. Upload to cloud (optional)
# ============================================================================
if [ -n "${GCS_BUCKET}" ]; then
    log_info "Uploading to Google Cloud Storage..."
    gsutil cp "${BACKUP_NAME}.tar.gz" "gs://${GCS_BUCKET}/backups/"
    log_info "Upload completed"
fi

if [ -n "${S3_BUCKET}" ]; then
    log_info "Uploading to AWS S3..."
    aws s3 cp "${BACKUP_NAME}.tar.gz" "s3://${S3_BUCKET}/backups/"
    log_info "Upload completed"
fi

# ============================================================================
# 8. Cleanup old backups
# ============================================================================
log_info "Cleaning up backups older than ${RETENTION_DAYS} days..."

find "${BACKUP_DIR}" -name "oma_backup_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete

REMAINING=$(find "${BACKUP_DIR}" -name "oma_backup_*.tar.gz" | wc -l)
log_info "Retention complete. ${REMAINING} backups remaining."

# ============================================================================
# 9. Send notification (optional)
# ============================================================================
if [ -n "${SLACK_WEBHOOK}" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"✅ OMA.AI backup completed: ${BACKUP_NAME} (${BACKUP_SIZE})\"}" \
        "${SLACK_WEBHOOK}"
fi

log_info "Backup completed successfully!"
log_info "Backup location: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

exit 0
