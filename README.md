# Wallapop → web propia

Extrae tus productos publicados en Wallapop y genera una **web HTML autónoma**
(`index.html`) con imágenes, buscador, filtro de precio, orden y gráfico. Esa
web la subes a cualquier hosting (GitHub Pages, Netlify, tu servidor...).

Incluye además un **panel Streamlit** local para actualizar y previsualizar.

## ⚠️ El scraping se ejecuta en local, no en Streamlit Cloud

Para leer *tus* productos hay que abrir Chrome con tu sesión de Wallapop. Eso
necesita una pantalla donde iniciar sesión, así que el scraper funciona en tu
ordenador, **no** en Streamlit Community Cloud. Lo que sí es desplegable en
cualquier sitio es el `index.html` que se genera.

## Archivos

- `scraper.py` — extrae los productos (con imagen) a `productos.json` y CSV.
- `generar_web.py` — convierte `productos.json` en `index.html` autónomo.
- `script.py` — panel Streamlit: actualizar + previsualizar + descargar.

## Instalación

```bash
cd wallapop
bash setup.sh
```

## Uso

```bash
source .venv/bin/activate
streamlit run script.py
```

1. Pulsa **Actualizar ahora**.
2. **La primera vez**, marca "Es la primera vez" e inicia sesión en la ventana
   de Chrome. La sesión queda guardada en `chrome-profile/` y no tendrás que
   volver a loguearte.
3. Filtra/ordena en la barra lateral y descarga **index.html** o CSV.

Alternativa por consola:

```bash
python scraper.py        # extrae productos.json
python generar_web.py    # genera index.html
```

## Publicar la web

Sube `index.html` a tu hosting. Para GitHub Pages, por ejemplo:

```bash
git init
git add index.html
git commit -m "Catálogo Wallapop"
git branch -M main
git remote add origin <URL-de-tu-repo>
git push -u origin main
# Activa Pages en Settings → Pages → rama main
```

> El `.gitignore` excluye el entorno virtual, el perfil de Chrome (tu sesión) y
> los CSV. **`index.html` y `productos.json` sí se pueden subir** si quieres
> publicar el catálogo.

## Personalizar

- Colores y estilo: variables CSS al inicio de la plantilla en `generar_web.py`
  (`--bg`, `--card`, `--accent`...).
- Título del catálogo: variable `TITULO` en `generar_web.py`.
- Campos extra: añádelos en `_extraer_items()` de `scraper.py` y muéstralos en
  la plantilla.
