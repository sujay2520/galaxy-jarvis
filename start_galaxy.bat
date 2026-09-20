@echo off
title Galaxy (Jarvis) - Starting...
color 0A

echo.
echo  ================================================================
echo       [*]  G A L A X Y   (J A R V I S)   S Y S T E M
echo       Permission-Based Autonomous Multi-Agent OS
echo  ================================================================
echo.

:: Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found. Install Python 3.10+ from python.org
    pause
    exit /b 1
)

:: Check Node.js (for Electron)
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo  [WARN] Node.js not found. Desktop app won't work, but web UI will.
)

:: Set Ollama model path
set OLLAMA_MODELS=F:\Ollama\models

:: Start Ollama if not running
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if %errorlevel% neq 0 (
    echo  [1/3] Starting Ollama (local LLM)...
    if exist "C:\Users\jarvis\AppData\Local\Programs\Ollama\ollama.exe" (
        start /B "" "C:\Users\jarvis\AppData\Local\Programs\Ollama\ollama.exe" serve
        timeout /t 3 /nobreak >nul
    ) else (
        echo  [WARN] Ollama not found. Cloud LLMs only.
    )
) else (
    echo  [1/3] Ollama already running.
)

:: Check if server already running
curl -s http://localhost:8000/api/status >nul 2>nul
if %errorlevel% equ 0 (
    echo  [2/3] Galaxy server already running.
    goto :open_ui
)

:: Start Galaxy server
echo  [2/3] Starting Galaxy server...
cd /d "F:\Jarvis AG"
start /B python run.py

:: Wait for server
echo  [3/3] Waiting for server to start...
:wait_loop
timeout /t 1 /nobreak >nul
curl -s http://localhost:8000/api/status >nul 2>nul
if %errorlevel% neq 0 goto :wait_loop

:open_ui
echo.
echo  ================================================================
echo       [OK] Galaxy is ready!
echo  ================================================================
echo.

:: Try Electron first, fall back to browser
if exist "F:\Jarvis AG\desktop\node_modules\.package-lock.json" (
    echo  [*] Launching desktop app...
    cd /d "F:\Jarvis AG\desktop"
    start /B npx electron .
) else (
    echo  [*] Opening in browser...
    start http://localhost:8000
)

echo.
echo  Web UI:    http://localhost:8000
echo  Phone:     http://YOUR-IP:8000 (same Wi-Fi)
echo  API Docs:  http://localhost:8000/docs
echo.
echo  Press Ctrl+C to stop the server.
echo.

:: Keep window open
cmd /k
