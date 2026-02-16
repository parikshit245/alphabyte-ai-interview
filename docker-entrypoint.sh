#!/bin/sh
set -e

echo "Starting backend application..."

echo "Starting server..."
exec node apps/backend/server.js
