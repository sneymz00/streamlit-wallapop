#!/bin/bash
# Wallapop -> web propia | Lanzador todo-en-uno (macOS / Linux).
# La PRIMERA vez crea el entorno e instala las dependencias; después solo abre
# el panel. La conexión con Chrome es automática (no hace falta abrir nada a mano).
#
# Uso:  bash iniciar.sh
set -e
cd "$(dirname "$0")"

# --- Localizar Python 3 ---
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "❌ No se encuentra Python 3. Instálalo desde https://www.python.org/downloads/"
  exit 1
fi

# --- Crear entorno e instalar dependencias (solo la 1ª vez) ---
if [ ! -f ".venv/bin/activate" ]; then
  echo "Creando entorno virtual e instalando dependencias (solo la primera vez)..."
  "$PY" -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

echo ""
echo "Iniciando el panel de Wallapop en el navegador..."
echo "Para cerrarlo, cierra esta ventana o pulsa Ctrl+C."
echo ""
streamlit run script.py
