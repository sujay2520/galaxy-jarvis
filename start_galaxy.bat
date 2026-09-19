@echo off
title Galaxy (Jarvis) Autonomous OS
echo ================================================================
echo        Starting Galaxy (Jarvis) Autonomous System
echo ================================================================
echo.

set OLLAMA_MODELS=F:\Ollama\models

:: Check if Ollama is running, if not start it
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Ollama server is already running with models on F:\
) else (
    echo [*] Starting Ollama local engine on F:\Ollama\models...
    start /B "" "C:\Users\jarvis\AppData\Local\Programs\Ollama\ollama.exe" serve
    timeout /t 3 /nobreak >nul
)

echo [*] Starting Galaxy Backend + Responsive Web UI...
echo.
python "F:\Jarvis AG\run.py"

pause
