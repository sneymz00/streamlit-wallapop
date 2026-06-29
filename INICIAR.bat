@echo off
REM ============================================================
REM  Wallapop -> web propia  |  Lanzador todo-en-uno (Windows)
REM  Doble clic en este archivo. La PRIMERA vez crea el entorno
REM  e instala las dependencias; despues solo abre el panel.
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

REM --- Localizar Python -------------------------------------------------
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo.
    echo [ERROR] No se ha encontrado Python.
    echo Instalalo desde https://www.python.org/downloads/
    echo y marca la casilla "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

REM --- Crear entorno e instalar dependencias (solo la 1a vez) -----------
if not exist ".venv\Scripts\activate.bat" (
    echo.
    echo Creando entorno virtual e instalando dependencias...
    echo (esto solo ocurre la primera vez, puede tardar 1-2 minutos)
    echo.
    %PY% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    call ".venv\Scripts\activate.bat"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Fallo la instalacion de dependencias.
        pause
        exit /b 1
    )
) else (
    call ".venv\Scripts\activate.bat"
)

REM --- Arrancar el panel ------------------------------------------------
echo.
echo Iniciando el panel de Wallapop en el navegador...
echo Para cerrarlo, cierra esta ventana o pulsa Ctrl+C.
echo.
streamlit run script.py

pause
