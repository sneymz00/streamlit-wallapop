@echo off
REM ============================================================
REM  Abre Google Chrome conectado al panel (puerto 9222) con un
REM  perfil dedicado que GUARDA tu sesion de Wallapop.
REM
REM  La PRIMERA vez, inicia sesion en Wallapop en la ventana que
REM  se abre. La sesion queda guardada en .\chrome-debug-profile
REM  y el panel reutilizara esa ventana.
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

set "PERFIL=%CD%\chrome-debug-profile"

REM --- Localizar chrome.exe en las rutas habituales --------------------
set "CHROME="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not defined CHROME if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not defined CHROME if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"

if not defined CHROME (
    echo.
    echo [ERROR] No se ha encontrado Google Chrome.
    echo Instalalo desde https://www.google.com/chrome/
    echo o edita la ruta CHROME en este archivo.
    echo.
    pause
    exit /b 1
)

echo Abriendo Chrome en modo panel (puerto 9222)...
start "" "%CHROME%" --remote-debugging-port=9222 --user-data-dir="%PERFIL%" "https://es.wallapop.com/app/catalog/published"

echo.
echo Listo.
echo  - Si es la primera vez, inicia sesion en Wallapop en esa ventana.
echo  - Dejala abierta y, en el panel, marca "Usar Chrome en modo debug".
echo.
