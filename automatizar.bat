@echo off
REM ============================================================
REM  Wallapop -> web propia | Ejecucion DESATENDIDA (Windows).
REM  Lo lanza el Programador de tareas (o doble clic para probar).
REM  Sincroniza, genera la web y publica en GitHub Pages.
REM  No muestra "pause": pensado para ejecutarse solo.
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

REM --- Localizar Python ---
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo [ERROR] No se ha encontrado Python. Instalalo desde https://www.python.org/downloads/
    exit /b 1
)

REM --- Crear entorno e instalar dependencias (solo la 1a vez) ---
if not exist ".venv\Scripts\activate.bat" (
    %PY% -m venv .venv
    call ".venv\Scripts\activate.bat"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call ".venv\Scripts\activate.bat"
)

REM --- Ejecutar el ciclo desatendido (pasa argumentos: p.ej. --no-publicar) ---
python run_auto.py %*
exit /b %errorlevel%
