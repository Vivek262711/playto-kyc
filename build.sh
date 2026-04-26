#!/usr/bin/env bash
# Build script for Render deployment
# This runs during the build phase on Render

set -o errexit  # Exit on error

echo "=== Installing backend dependencies ==="
cd backend
pip install -r requirements.txt

echo "=== Installing frontend dependencies ==="
cd ../frontend
npm install

echo "=== Building frontend ==="
npm run build

echo "=== Running Django collectstatic ==="
cd ../backend
python manage.py collectstatic --noinput

echo "=== Running Django migrations ==="
python manage.py migrate

echo "=== Seeding demo data ==="
python seed.py

echo "=== Build complete! ==="
