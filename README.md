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
Ahora la conexión es **automática**: el panel abre Chrome por ti (con un perfil
dedicado que guarda tu sesión). No hay que abrir ni dejar abierta ninguna ventana
a mano.

1. En el panel, pulsa **"Sincronizar Datos"**.
2. **Solo la primera vez:** marca antes en la barra lateral la casilla
   **"Es la primera vez"**. Se abrirá una ventana de Chrome en Wallapop; inicia
   sesión ahí con tu usuario y contraseña. Tu sesión queda guardada y no tendrás
   que repetirlo.
3. El programa leerá tus productos y generará la web. En las siguientes veces solo
   tienes que pulsar **"Sincronizar Datos"**: Chrome se abre y se reutiliza solo.
4. Usa la barra lateral para **filtrar y ordenar**, y pulsa el botón para
   **descargar `index.html`** (tu web) o el CSV.

¡Ya tienes tu web `index.html` lista en la carpeta!

> Los atajos `abrir_chrome_debug.bat`/`.sh` siguen existiendo por si quieres abrir
> la ventana de Chrome manualmente, pero **ya no hacen falta**.

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

Una vez conectado el repositorio, tienes dos formas de subir los cambios:

- **Desde el panel (lo más cómodo):** pulsa **"Publicar en GitHub Pages"** en la
  barra lateral. Regenera la web y la sube automáticamente.
- **Doble clic en `publicar.bat`.**

La **primera vez** que publiques, Git puede abrir una ventana para que inicies
sesión en GitHub; hazlo una vez y quedará recordado.

---

## Parte 5 — Automatizar en Windows (desatendido, 1 vez al día)

Para que el PC Windows actualice y publique el catálogo **solo**, sin que abras nada:

1. **Login una sola vez.** Doble clic en `abrir_chrome_debug.bat`, inicia sesión en
   Wallapop y cierra la ventana. La sesión queda guardada en `chrome-debug-profile`.
2. **Deja git listo para publicar solo** (una vez): la carpeta debe estar conectada a
   tu repo de GitHub (Parte 4) y con las credenciales recordadas (al hacer el primer
   `git push` a mano, Windows las guarda en el Administrador de credenciales).
3. **Crea la tarea programada.** Clic derecho en `programar_windows.ps1` →
   *Ejecutar con PowerShell* (una sola vez). Crea una tarea diaria a las 09:00 que
   ejecuta `automatizar.bat` (sincroniza → genera `index.html` → publica en GitHub).
   Para otra hora, edita `$Hora` dentro del `.ps1`.

Notas:
- La tarea se ejecuta **con tu usuario y solo cuando has iniciado sesión en Windows**
  (Chrome necesita escritorio). Si el PC está bloqueado pero con sesión abierta, funciona.
- Cada ejecución deja un registro en `run_auto.log`. Códigos: `0` OK, `1` error,
  `2` sin sesión/sin productos (vuelve al paso 1).
- Para probar sin esperar a la hora: doble clic en `automatizar.bat` (o
  `automatizar.bat --no-publicar` para no subir nada).

---

## Resumen rápido (para el día a día)

| Quiero… | En Windows | En macOS |
|---|---|---|
| Abrir el programa | doble clic en **`INICIAR.bat`** | `bash iniciar.sh` |
| Actualizar mis productos | botón **"Sincronizar Datos"** | botón **"Sincronizar Datos"** |
| Iniciar sesión (solo la 1ª vez) | marca *"Es la primera vez"* y pulsa **"Sincronizar Datos"** | igual |
| Publicar la web online | doble clic en **`publicar.bat`** | `bash publicar.sh` |

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
La primera vez, marca *"Es la primera vez"* en la barra lateral y pulsa
**"Sincronizar Datos"**: se abrirá Chrome, inicia sesión en Wallapop en esa
ventana y espera a que termine. Si ya iniciaste sesión antes, simplemente vuelve a
pulsar "Sincronizar Datos" (Chrome se abre solo y reutiliza tu sesión).

---

## ¿Qué hace cada archivo?

- **`INICIAR.bat`** (Windows) / **`iniciar.sh`** (macOS) — instala todo (la 1ª vez)
  y abre el panel. Es el botón principal.
- `abrir_chrome_debug.bat`/`.sh` — *(opcional)* abre Chrome con tu sesión de Wallapop
  a mano. Ya no hace falta: el panel lo abre automáticamente.
- **`publicar.bat`** / **`publicar.sh`** — sube la web a GitHub Pages (tras configurarlo una vez).
- `script.py` — el panel.
- `scraper.py` — lee tus productos de Wallapop (abre Chrome automáticamente).
- `generar_web.py` — convierte los productos en la web `index.html`.
- `run_auto.py` — ciclo **desatendido** (sincroniza + genera + publica), sin panel.
- **`automatizar.bat`** / `automatizar.sh` — lanza `run_auto.py` (lo usa la tarea programada).
- **`programar_windows.ps1`** — crea la tarea diaria en el Programador de tareas (Windows).

## Personalizar la web

- Colores y estilo: variables CSS al inicio de la plantilla en `generar_web.py`
  (`--bg`, `--card`, `--accent`…).
- Título del catálogo: variable `TITULO` en `generar_web.py`.

---

### Nota para macOS / Linux

Arranca todo con **`bash iniciar.sh`** (crea el entorno la 1ª vez y abre el panel).
La conexión con Chrome es automática, así que no necesitas abrir nada a mano; para
publicar usa `bash publicar.sh`. Si Chrome está en una ruta no habitual, puedes
indicarla con la variable de entorno `CHROME_BIN`.
