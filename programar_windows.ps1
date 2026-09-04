# ============================================================
#  Registra en el Programador de tareas de Windows una tarea que
#  ejecuta automatizar.bat UNA VEZ AL DIA (sincroniza Wallapop y
#  publica el catalogo). Ejecutar UNA sola vez.
#
#  Como ejecutarlo:
#    - Clic derecho en este archivo > "Ejecutar con PowerShell", o
#    - En PowerShell:  powershell -ExecutionPolicy Bypass -File programar_windows.ps1
#
#  Se ejecuta con TU usuario y SOLO cuando has iniciado sesion en
#  Windows (Chrome necesita el escritorio). Cambia $Hora si quieres
#  otra hora del dia.
# ============================================================

$ErrorActionPreference = "Stop"

$Hora   = "09:00"                      # <-- hora de la ejecucion diaria
$Nombre = "Wallapop - catalogo diario"

$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Bat = Join-Path $Dir "automatizar.bat"

if (-not (Test-Path $Bat)) {
    Write-Error "No se encuentra automatizar.bat en $Dir"
    exit 1
}

$Accion   = New-ScheduledTaskAction -Execute $Bat -WorkingDirectory $Dir
$Disparador = New-ScheduledTaskTrigger -Daily -At $Hora
$Ajustes  = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask -TaskName $Nombre -Action $Accion -Trigger $Disparador `
    -Settings $Ajustes -Description "Sincroniza Wallapop y publica el catalogo en GitHub Pages" -Force | Out-Null

Write-Host ""
Write-Host "OK: tarea '$Nombre' creada. Se ejecutara cada dia a las $Hora." -ForegroundColor Green
Write-Host "Puedes verla/ejecutarla a mano en 'Programador de tareas' (taskschd.msc)."
Write-Host ""
Write-Host "IMPORTANTE (solo la 1a vez): inicia sesion en Wallapop ejecutando"
Write-Host "abrir_chrome_debug.bat, entra con tu usuario y cierra la ventana."
