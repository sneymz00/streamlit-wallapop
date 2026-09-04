"""
Runner DESATENDIDO de Wallapop (para el Programador de tareas de Windows).

Hace todo el ciclo sin interfaz ni clics:
  1. Conecta con Chrome automáticamente (lo abre en modo depuración si no está)
     y extrae tus productos usando tu sesión guardada.
  2. Regenera index.html (la web).
  3. Publica en GitHub Pages (git add/commit/push), salvo que pases --no-publicar.

Uso:
    python run_auto.py                # sincroniza + genera + publica
    python run_auto.py --no-publicar  # sincroniza + genera (sin subir)

Requisito previo (una sola vez): tener la sesión de Wallapop iniciada en el
perfil dedicado. Si nunca has iniciado sesión en este PC, ejecuta una vez
abrir_chrome_debug.bat, inicia sesión en Wallapop y cierra la ventana.

Códigos de salida: 0 = OK · 1 = error · 2 = sin sesión / sin productos activos.
"""

import os
import sys
import datetime as dt
import subprocess

from scraper import extraer_productos, DEBUG_PORT
import generar_web

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "run_auto.log")


def log(msg: str) -> None:
    """Escribe en consola y en run_auto.log con marca de tiempo."""
    linea = f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(linea, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
    except OSError:
        pass


def _git(args):
    return subprocess.run(["git"] + args, cwd=BASE_DIR, capture_output=True, text=True)


def publicar_git() -> bool:
    """Sube index.html (y productos.json) a GitHub Pages. Devuelve True si OK."""
    if not os.path.exists(os.path.join(BASE_DIR, "index.html")):
        log("No hay index.html; no se publica.")
        return False
    if not os.path.isdir(os.path.join(BASE_DIR, ".git")):
        log("La carpeta no está conectada a git; no se publica. (Configúralo una vez, ver README.)")
        return False

    # La identidad de AUTOR se fija a nivel LOCAL del repo (una sola persona):
    #   git config --local user.name  "<nombre>"
    #   git config --local user.email "<email>"
    # NO inventamos ninguna identidad aquí, para no crear un segundo autor.
    if not _git(["config", "user.email"]).stdout.strip():
        log(
            "Sin identidad de git en esta carpeta. Fíjala UNA vez y reintenta:\n"
            '  git config --local user.name  "<nombre>"\n'
            '  git config --local user.email "<email>"'
        )
        return False

    _git(["add", "index.html"])
    if os.path.exists(os.path.join(BASE_DIR, "productos.json")):
        _git(["add", "productos.json"])

    if _git(["diff", "--cached", "--quiet"]).returncode == 0:
        log("Sin cambios que publicar.")
        return True

    _git(["commit", "-m", f"Actualiza catálogo ({dt.datetime.now():%d/%m/%Y %H:%M})"])
    push = _git(["push"])
    if push.returncode == 0:
        log("Publicado en GitHub Pages.")
        return True
    log("ERROR al hacer push:\n" + (push.stderr or push.stdout or "desconocido"))
    return False


def main() -> int:
    publicar = "--no-publicar" not in sys.argv
    log("=== Inicio run_auto (desatendido) ===")
    try:
        # esperar_login_segundos=0: desatendido, no hay nadie para iniciar sesión.
        df = extraer_productos(esperar_login_segundos=0, adjuntar_puerto=DEBUG_PORT)
    except Exception as e:  # noqa: BLE001 (queremos que la tarea no reviente)
        log(f"ERROR en la extracción: {e}")
        return 1

    n = 0 if df is None else len(df)
    if not n:
        log(
            "No se detectaron productos activos. Puede que la sesión de Wallapop "
            "haya caducado: inicia sesión una vez con abrir_chrome_debug.bat."
        )
        return 2

    log(f"Productos activos: {n}. Generando web...")
    try:
        generar_web.generar()
    except Exception as e:  # noqa: BLE001
        log(f"ERROR al generar la web: {e}")
        return 1

    if publicar:
        ok = publicar_git()
        return 0 if ok else 1

    log("Hecho (sin publicar, --no-publicar).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
