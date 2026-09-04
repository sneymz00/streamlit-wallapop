#!/bin/bash
# Ejecucion DESATENDIDA (macOS / Linux): sincroniza, genera la web y publica.
# Equivalente a automatizar.bat. Útil para probar el runner en local o para
# programarlo con cron/launchd. Pasa --no-publicar para no subir a GitHub.
#
# Uso:  bash automatizar.sh [--no-publicar]
set -e
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi

if [ ! -f ".venv/bin/activate" ]; then
  "$PY" -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

python run_auto.py "$@"
