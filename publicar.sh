#!/bin/bash
# Publica el catálogo (index.html) en tu repositorio de GitHub Pages.
#
# Uso:  bash publicar.sh ["mensaje opcional"]
#
# Requisito previo (una sola vez): tener esta carpeta conectada a un repo de
# GitHub. Si no lo está, el script te indica los comandos.
set -e
cd "$(dirname "$0")"

if [ ! -f index.html ]; then
  echo "❌ No existe index.html todavía."
  echo "   Pulsa 'Sincronizar Datos y Generar Web' en el panel para generarlo y vuelve a ejecutar."
  exit 1
fi

if [ ! -d .git ]; then
  echo "❌ Esta carpeta aún no es un repositorio git."
  echo "   Configúralo una sola vez:"
  echo ""
  echo "     git init"
  echo "     git add ."
  echo "     git commit -m 'Catálogo Wallapop'"
  echo "     git branch -M main"
  echo "     git remote add origin <URL-de-tu-repo-en-GitHub>"
  echo "     git push -u origin main"
  echo ""
  echo "   Después, activa GitHub Pages en Settings → Pages → rama main."
  exit 1
fi

MSG="${1:-Actualiza catálogo Wallapop ($(date '+%d/%m/%Y %H:%M'))}"

git add index.html
[ -f productos.json ] && git add productos.json

if git diff --cached --quiet; then
  echo "ℹ️ No hay cambios nuevos que publicar."
  exit 0
fi

git commit -m "$MSG"
git push

echo "✅ Catálogo publicado. En 1-2 minutos estará actualizado en tu web."
