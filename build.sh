#!/usr/bin/env bash
# Render.com build script
set -o errexit

# Install Python deps
pip install --upgrade pip
pip install -r requirements.txt

# Build frontend
cd web
npm install
npm run build
cd ..

echo "Build complete."
