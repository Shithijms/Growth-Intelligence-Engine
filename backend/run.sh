#!/usr/bin/env bash
# Run backend from repo root or backend dir. Usage: ./run.sh
set -e
cd "$(dirname "$0")"
if [ -d .venv ]; then
  source .venv/bin/activate
fi
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
