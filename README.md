# Wallapop → tu propia web (Windows)

Esta herramienta lee los productos que tienes publicados en Wallapop y genera una
**página web autónoma** (`index.html`) con fotos, buscador, filtro de precio,
orden y un gráfico. Esa página la puedes subir a cualquier hosting gratuito
(GitHub Pages, Netlify, tu servidor…).

Incluye un **panel** (se abre en tu navegador) para actualizar los productos y
previsualizar la web antes de publicarla.

> **Lo único que tienes que recordar:** para usar el programa, haz doble clic en
> **`INICIAR.bat`**. Nada más.

---

## Parte 1 — Instalaciones necesarias (solo la primera vez)

Hay que instalar **dos programas** en el ordenador. Si ya los tienes, salta al
paso correspondiente.

### 1.1 Instalar Python

1. Entra en https://www.python.org/downloads/
2. Pulsa el botón amarillo **"Download Python"** (la versión que te ofrezca vale).
3. Abre el archivo descargado.
4. **MUY IMPORTANTE:** antes de pulsar "Install Now", marca abajo la casilla
   **☑ "Add python.exe to PATH"**. Si no la marcas, el programa no funcionará.
5. Pulsa **"Install Now"** y espera a que termine. Cierra la ventana al acabar.

### 1.2 Instalar Google Chrome

1. Entra en https://www.google.com/chrome/
2. Pulsa **"Descargar Chrome"** e instálalo con las opciones por defecto.

*(Si ya usas Chrome normalmente, no tienes que hacer nada.)*

### 1.3 (Opcional) Instalar Git — solo si vas a publicar la web online

Solo lo necesitas si quieres subir tu catálogo a internet con GitHub Pages
(ver Parte 4). Para usar el programa en local **no hace falta**.

1. Entra en https://git-scm.com/download/win
2. Descárgalo e instálalo pulsando "Next" en todas las pantallas (las opciones
   por defecto están bien).

---

## Parte 2 — Arrancar el programa

1. Abre la carpeta `wallapop`.
2. Haz **doble clic en `INICIAR.bat`**.
3. **La primera vez** se abrirá una ventana negra que instala todo lo necesario
   automáticamente. Tarda 1 o 2 minutos. **No la cierres**, espera.
4. Cuando termine, se abrirá solo el **panel** en tu navegador.

> Las siguientes veces, `INICIAR.bat` abrirá el panel directamente en segundos.

Si al hacer doble clic ves un mensaje de que falta Python, vuelve al paso 1.1 y
asegúrate de haber marcado **"Add python.exe to PATH"**.

---

## Parte 3 — Extraer tus productos y generar la web

Para leer **tus** productos, el programa necesita tu sesión iniciada en Wallapop.
Esto se hace con un Chrome especial (solo tienes que iniciar sesión una vez).

1. Haz **doble clic en `abrir_chrome_debug.bat`**. Se abrirá una ventana de
   Chrome en la página de Wallapop.
2. **Solo la primera vez:** inicia sesión en Wallapop en esa ventana con tu
   usuario y contraseña. Tu sesión queda guardada y no tendrás que volver a
   hacerlo.
3. **Deja esa ventana de Chrome abierta.**
4. Vuelve al **panel** (la pestaña del navegador que abrió `INICIAR.bat`).
5. Comprueba que está marcada la casilla **"Usar Chrome en modo debug"**.
6. Pulsa **"Actualizar ahora"**. El programa leerá tus productos.
7. Usa la barra lateral para **filtrar y ordenar**, y pulsa el botón para
   **descargar `index.html`** (tu web) o el CSV.

¡Ya tienes tu web `index.html` lista en la carpeta!

---

## Parte 4 — (Opcional) Publicar la web en internet

Tu `index.html` funciona haciéndole doble clic, pero si quieres una dirección
web pública y gratuita puedes usar **GitHub Pages**.

### Configuración (solo una vez)

1. Crea una cuenta gratis en https://github.com y crea un repositorio nuevo.
2. Necesitas Git instalado (Parte 1.3).
3. Abre la carpeta `wallapop`, haz clic en la barra de direcciones del
   explorador, escribe `cmd` y pulsa Enter. Se abrirá una ventana de comandos
   en esa carpeta. Pega estos comandos uno a uno (cambia la URL por la de tu
   repositorio):

   ```
   git init
   git add .
   git commit -m "Catalogo Wallapop"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
   git push -u origin main
   ```

4. En GitHub, ve a tu repositorio → **Settings → Pages** y activa Pages en la
   rama **main**. En unos minutos tu web estará online.

### Republicar después de actualizar

Cada vez que regeneres la web y quieras subir los cambios, haz **doble clic en
`publicar.bat`**.

---

## Resumen rápido (para el día a día)

| Quiero… | Hago… |
|---|---|
| Abrir el programa | doble clic en **`INICIAR.bat`** |
| Iniciar sesión en Wallapop | doble clic en **`abrir_chrome_debug.bat`** |
| Actualizar mis productos | botón **"Actualizar ahora"** en el panel |
| Publicar la web online | doble clic en **`publicar.bat`** |

---

## Preguntas frecuentes

**Al abrir un `.bat` aparece un aviso azul de Windows ("Windows protegió tu PC").**
Es normal con archivos descargados. Pulsa **"Más información"** y luego
**"Ejecutar de todas formas"**.

**Dice que no encuentra Python.**
No marcaste "Add python.exe to PATH" al instalarlo. Reinstala Python (Parte 1.1)
marcando esa casilla.

**Dice que no encuentra Chrome.**
Instala Google Chrome (Parte 1.2). Si lo tienes en una ruta no habitual, puedes
editar la ruta dentro de `abrir_chrome_debug.bat`.

**El panel no lee mis productos.**
Asegúrate de haber abierto Chrome con `abrir_chrome_debug.bat`, de haber iniciado
sesión en Wallapop en esa ventana y de **dejarla abierta** mientras pulsas
"Actualizar ahora".

---

## ¿Qué hace cada archivo?

- **`INICIAR.bat`** — instala todo (la 1ª vez) y abre el panel. Es el botón principal.
- **`abrir_chrome_debug.bat`** — abre Chrome con tu sesión de Wallapop guardada.
- **`publicar.bat`** — sube la web a GitHub Pages (tras configurarlo una vez).
- `script.py` — el panel.
- `scraper.py` — lee tus productos de Wallapop.
- `generar_web.py` — convierte los productos en la web `index.html`.

## Personalizar la web

- Colores y estilo: variables CSS al inicio de la plantilla en `generar_web.py`
  (`--bg`, `--card`, `--accent`…).
- Título del catálogo: variable `TITULO` en `generar_web.py`.

---

### Nota para macOS / Linux

En otros sistemas, instala con `bash setup.sh`, arranca con
`source .venv/bin/activate && streamlit run script.py`, abre Chrome con
`bash abrir_chrome_debug.sh` y publica con `bash publicar.sh`.
