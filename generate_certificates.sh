#!/bin/bash
# Script to generate SSL certificates for the Luno MCP server WebSocket transport
# This script creates self-signed certificates for local development and testing

# Create certificates directory if it doesn't exist
mkdir -p ./certs

# Set certificate parameters
CERT_DAYS=365
CERT_FILE="./certs/server.crt"
KEY_FILE="./certs/server.key"
SUBJECT="/CN=localhost/O=Luno MCP Server/OU=Development"

echo "Generating self-signed certificate for Luno MCP WebSocket server..."

# Generate a private key
openssl genrsa -out $KEY_FILE 2048

# Generate a self-signed certificate
openssl req -new -x509 -key $KEY_FILE -out $CERT_FILE -days $CERT_DAYS -subj "$SUBJECT"

# Set appropriate permissions
chmod 600 $KEY_FILE
chmod 644 $CERT_FILE

echo "Certificate generated successfully:"
echo "Certificate file: $CERT_FILE"
echo "Key file: $KEY_FILE"
echo 
echo "These certificates are self-signed and should only be used for development."
echo "For production, use certificates from a trusted Certificate Authority."
echo
echo "To use with the WebSocket transport, run:"
echo "python -m src.main --transport websocket --ssl-cert $CERT_FILE --ssl-key $KEY_FILE"
