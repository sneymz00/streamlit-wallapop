#!/bin/bash
# Abre una ventana de Google Chrome conectada al panel (puerto 9222), con un
# perfil dedicado que GUARDA tu sesión de Wallapop.
#
# Uso:  bash abrir_chrome_debug.sh
#
# La PRIMERA vez, inicia sesión en Wallapop en la ventana que se abre. La sesión
# queda guardada en ./chrome-debug-profile y el panel reutilizará esa ventana
# (no abrirá sesiones nuevas).
set -e
cd "$(dirname "$0")"

PERFIL="$(pwd)/chrome-debug-profile"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if [ ! -x "$CHROME" ]; then
  echo "❌ No encuentro Google Chrome en:"
  echo "   $CHROME"
  echo "Instálalo o ajusta la ruta en este script."
  exit 1
fi

echo "🚀 Abriendo Chrome en modo panel (puerto 9222)..."
"$CHROME" \
  --remote-debugging-port=9222 \
  --user-data-dir="$PERFIL" \
  "https://es.wallapop.com/app/catalog/published" >/dev/null 2>&1 &

echo "✅ Listo."
echo "   - Si es la primera vez, inicia sesión en Wallapop en esa ventana."
echo "   - Déjala abierta y, en el panel, marca 'Usar mi Chrome abierto'."
