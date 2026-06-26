#!/bin/bash
# Instala las dependencias en un entorno virtual dentro de esta carpeta.
# Uso:  bash setup.sh
set -e
cd "$(dirname "$0")"

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Dependencias instaladas."
echo "Para arrancar el panel:"
echo "   source .venv/bin/activate && streamlit run script.py"
