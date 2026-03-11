#!/usr/bin/env bash
# ============================================================
# Generate self-signed SSL certificates for development/testing.
# For production, replace these with certificates from a trusted CA
# (e.g., Let's Encrypt via certbot).
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERT_FILE="${SCRIPT_DIR}/cert.pem"
KEY_FILE="${SCRIPT_DIR}/key.pem"

if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "Certificates already exist. Delete them first to regenerate."
    echo "  rm ${CERT_FILE} ${KEY_FILE}"
    exit 0
fi

echo "Generating self-signed SSL certificate (valid for 365 days)..."

openssl req -x509 -nodes \
    -days 365 \
    -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "/C=CL/ST=Dev/L=Dev/O=AI-Tutoring-System/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

echo "Certificates generated:"
echo "  Certificate: ${CERT_FILE}"
echo "  Private key: ${KEY_FILE}"
echo ""
echo "WARNING: These are self-signed certificates for development only."
echo "For production, use Let's Encrypt or another trusted CA."
