#!/bin/sh

SSL_DIR="/etc/ssl"
CERT_FILE="$SSL_DIR/certs/nginx-selfsigned.crt"
KEY_FILE="$SSL_DIR/private/nginx-selfsigned.key"

if [ ! -f $CERT_FILE ] || [ ! -f $KEY_FILE ]; then
	openssl req \
		-x509 \
		-nodes \
		-days 365 \
		-newkey rsa:2048 \
		-keyout $KEY_FILE \
		-out $CERT_FILE \
		-subj "/C=FR/ST=Paris/L=Paris/O=42/OU=42/CN=localhost"
fi

nginx -g "daemon off;"