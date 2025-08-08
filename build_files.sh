#!/bin/bash
# Build script for Vercel deployment

# Install dependencies
pip install -r requirements-vercel.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create build output
mkdir -p build
cp -r luxestays_project build/
cp -r website build/
cp -r templates build/
cp -r staticfiles build/
cp manage.py build/
cp requirements-vercel.txt build/requirements.txt 