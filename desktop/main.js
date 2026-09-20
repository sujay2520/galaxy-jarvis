const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain } = require('electron');
const path = require('path');
const { spawn, execSync } = require('child_process');
const http = require('http');
const fs = require('fs');

let mainWindow;
let splashWindow;
let tray = null;
let pythonProcess = null;
let ollamaProcess = null;
let isQuitting = false;

const isWin = process.platform === 'win32';
const rootDir = path.join(__dirname, '..');

const pythonPaths = [
    'python',
    'C:\\Python314\\python.exe',
    'C:\\Python3\\python.exe',
    '/usr/bin/python3'
];

const ollamaPath = isWin 
    ? 'C:\\Users\\jarvis\\AppData\\Local\\Programs\\Ollama\\ollama.exe' 
    : 'ollama';

function findExecutable(paths) {
    for (const p of paths) {
        try {
            if (p === 'python' || p === 'ollama') {
                const cmd = isWin ? `where ${p}` : `which ${p}`;
                execSync(cmd, { stdio: 'ignore' });
                return p;
            } else if (fs.existsSync(p)) {
                return p;
            }
        } catch (e) {}
    }
    return paths[0];
}

function startOllama() {
    const exePath = findExecutable([ollamaPath, 'ollama']);
    const env = { ...process.env };
    if (isWin) {
        env.OLLAMA_MODELS = 'F:\\Ollama\\models';
    }
    
    try {
        ollamaProcess = spawn(exePath, ['serve'], { env, stdio: 'ignore', windowsHide: true });
    } catch (e) {
        console.error('Failed to start Ollama:', e);
    }
}

function startPython() {
    const pyPath = findExecutable(pythonPaths);
    try {
        pythonProcess = spawn(pyPath, ['run.py'], { cwd: rootDir, stdio: 'ignore', windowsHide: true });
    } catch (e) {
        console.error('Failed to start Python:', e);
    }
}

function killProcesses() {
    if (pythonProcess) {
        try { pythonProcess.kill(); } catch (e) {}
    }
    if (ollamaProcess) {
        try { ollamaProcess.kill(); } catch (e) {}
    }
    
    if (isWin) {
        try { execSync('taskkill /F /IM ollama.exe', { stdio: 'ignore' }); } catch(e){}
    } else {
        try { execSync('pkill ollama', { stdio: 'ignore' }); } catch(e){}
    }
}

function pollServer(callback) {
    const check = () => {
        const req = http.get('http://localhost:8000/api/status', (res) => {
            if (res.statusCode === 200 || res.statusCode === 404) {
                callback();
            } else {
                setTimeout(check, 500);
            }
        }).on('error', () => {
            setTimeout(check, 500);
        });
        req.end();
    };
    check();
}

function createSplashWindow() {
    splashWindow = new BrowserWindow({
        width: 400,
        height: 300,
        transparent: true,
        frame: false,
        alwaysOnTop: true,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        }
    });
    splashWindow.loadFile('splash.html');
}

function createMainWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        show: false,
        titleBarStyle: 'hidden',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true
        }
    });

    mainWindow.loadURL('http://localhost:8000');
    
    mainWindow.on('close', (event) => {
        if (!isQuitting) {
            event.preventDefault();
            mainWindow.hide();
        }
    });
}

function createTray() {
    tray = new Tray(nativeImage.createEmpty()); 
    const contextMenu = Menu.buildFromTemplate([
        { label: 'Open Galaxy', click: () => mainWindow.show() },
        { label: 'Restart Server', click: () => {
            killProcesses();
            startOllama();
            startPython();
            mainWindow.reload();
        }},
        { label: 'Quit', click: () => {
            isQuitting = true;
            app.quit();
        }}
    ]);
    tray.setToolTip('Galaxy');
    tray.setContextMenu(contextMenu);
    
    tray.on('click', () => {
        mainWindow.show();
    });
}

app.whenReady().then(() => {
    createSplashWindow();
    startOllama();
    startPython();
    
    pollServer(() => {
        createMainWindow();
        createTray();
        mainWindow.show();
        if (splashWindow) {
            splashWindow.close();
            splashWindow = null;
        }
    });

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0 && mainWindow) {
            mainWindow.show();
        }
    });
});

app.on('window-all-closed', () => {});

app.on('before-quit', () => {
    isQuitting = true;
    killProcesses();
});

process.on('uncaughtException', (error) => {
    console.error('Uncaught exception:', error);
});
