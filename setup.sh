#!/bin/bash

# Exit on any error
set -e

echo "🐍 Setting up Python environment..."

# -------------------------------------------------
# Create & activate virtual environment
# -------------------------------------------------
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

# Upgrade pip tooling
pip install --upgrade pip setuptools wheel

# -------------------------------------------------
# Install backend dependencies
# -------------------------------------------------
pip install \
  fastapi \
  uvicorn[standard] \
  sqlalchemy \
  psycopg2-binary \
  jinja2 \
  python-multipart \
  pydantic \
  httpx \
  alembic

# -------------------------------------------------
# Project folders (if missing)
# -------------------------------------------------
mkdir -p app/static/css
mkdir -p app/static/js
mkdir -p app/templates
mkdir -p content

# -------------------------------------------------
# Freeze Python dependencies
# -------------------------------------------------
pip freeze > requirements.txt

# Deactivate venv
deactivate

echo "✅ Python dependencies installed and saved to requirements.txt"
echo "📁 Created folders: app/static/css, app/static/js, app/templates, content"
echo ""
echo "👉 Activate env:  source venv/bin/activate"
echo "👉 Run dev server: uvicorn app.main:app --reload"