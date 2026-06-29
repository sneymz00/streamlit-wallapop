@echo off
REM ============================================================
REM  Publica el catalogo (index.html) en tu repo de GitHub Pages.
REM  Uso: doble clic, o  publicar.bat "mensaje opcional"
REM
REM  Requisito previo (una sola vez): tener esta carpeta conectada
REM  a un repo de GitHub. Si no lo esta, el script te lo indica.
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

if not exist "index.html" (
    echo [ERROR] Todavia no existe index.html.
    echo Genera la web desde el panel y vuelve a ejecutar.
    pause
    exit /b 1
)

if not exist ".git" (
    echo [ERROR] Esta carpeta aun no es un repositorio git.
    echo Configuralo una sola vez:
    echo.
    echo     git init
    echo     git add .
    echo     git commit -m "Catalogo Wallapop"
    echo     git branch -M main
    echo     git remote add origin URL-DE-TU-REPO
    echo     git push -u origin main
    echo.
    echo Despues, activa GitHub Pages en Settings - Pages - rama main.
    pause
    exit /b 1
)

set "MSG=%~1"
if "%MSG%"=="" set "MSG=Actualiza catalogo Wallapop"

git add index.html
if exist "productos.json" git add productos.json

git diff --cached --quiet
if not errorlevel 1 (
    echo No hay cambios nuevos que publicar.
    pause
    exit /b 0
)

git commit -m "%MSG%"
git push

echo.
echo Catalogo publicado. En 1-2 minutos estara actualizado en tu web.
pause
