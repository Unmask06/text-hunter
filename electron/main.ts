import { app, BrowserWindow, ipcMain } from 'electron';
import { autoUpdater } from 'electron-updater';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

let mainWindow: BrowserWindow | null = null;
let sidecarProcess: ChildProcess | null = null;

const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

function getSidecarPath(): string {
  if (isDev) {
    const devPath = path.join(__dirname, '..', 'backend', 'dist', 'main.exe');
    if (fs.existsSync(devPath)) {
      return devPath;
    }
    return path.join(__dirname, '..', 'backend', 'dist', 'main.exe');
  }
  return path.join(process.resourcesPath, 'sidecar', 'main.exe');
}

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 950,
    resizable: true,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    icon: path.join(__dirname, '..', 'build', 'icons', 'icon.ico'),
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'frontend', 'dist', 'index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function spawnSidecar(): void {
  if (sidecarProcess) {
    console.log('[electron] Sidecar already running, skipping spawn');
    return;
  }

  const sidecarPath = getSidecarPath();
  console.log('[electron] Spawning sidecar from:', sidecarPath);

  if (!fs.existsSync(sidecarPath)) {
    console.error('[electron] Sidecar executable not found at:', sidecarPath);
    return;
  }

  sidecarProcess = spawn(sidecarPath, [], {
    stdio: ['pipe', 'pipe', 'pipe'],
    windowsHide: true,
  });

  sidecarProcess.stdout?.on('data', (data: Buffer) => {
    console.log('[sidecar stdout]', data.toString().trim());
  });

  sidecarProcess.stderr?.on('data', (data: Buffer) => {
    console.error('[sidecar stderr]', data.toString().trim());
  });

  sidecarProcess.on('error', (err: Error) => {
    console.error('[electron] Sidecar process error:', err);
  });

  sidecarProcess.on('exit', (code: number | null) => {
    console.log('[electron] Sidecar exited with code:', code);
    sidecarProcess = null;
  });

  console.log('[electron] Sidecar spawned successfully');
}

function shutdownSidecar(): void {
  if (sidecarProcess) {
    console.log('[electron] Shutting down sidecar...');
    
    try {
      sidecarProcess.stdin?.write('sidecar shutdown\n');
    } catch (err) {
      console.error('[electron] Failed to write to sidecar stdin:', err);
    }

    setTimeout(() => {
      if (sidecarProcess) {
        sidecarProcess.kill('SIGTERM');
        sidecarProcess = null;
      }
    }, 1000);
  }
}

function toggleFullscreen(): void {
  if (mainWindow) {
    const isFullScreen = mainWindow.isFullScreen();
    mainWindow.setFullScreen(!isFullScreen);
  }
}

ipcMain.handle('sidecar:start', (): string => {
  spawnSidecar();
  return 'Sidecar spawned';
});

ipcMain.handle('sidecar:shutdown', (): string => {
  shutdownSidecar();
  return 'Sidecar shutdown initiated';
});

ipcMain.handle('window:toggleFullscreen', (): void => {
  toggleFullscreen();
});

ipcMain.handle('app:getVersion', (): string => {
  return app.getVersion();
});

ipcMain.handle('app:isPackaged', (): boolean => {
  return app.isPackaged;
});

ipcMain.on('update:quitAndInstall', (): void => {
  autoUpdater.quitAndInstall();
});

autoUpdater.autoDownload = true;
autoUpdater.autoInstallOnAppQuit = true;

autoUpdater.on('checking-for-update', () => {
  console.log('[electron] Checking for updates...');
});

autoUpdater.on('update-available', (info) => {
  console.log('[electron] Update available:', info.version);
  mainWindow?.webContents.send('update:available', info);
});

autoUpdater.on('update-not-available', () => {
  console.log('[electron] No updates available');
});

autoUpdater.on('download-progress', (progress) => {
  console.log(`[electron] Download progress: ${progress.percent}%`);
  mainWindow?.webContents.send('update:progress', progress);
});

autoUpdater.on('update-downloaded', (info) => {
  console.log('[electron] Update downloaded:', info.version);
  mainWindow?.webContents.send('update:downloaded', info);
});

autoUpdater.on('error', (err) => {
  console.error('[electron] Auto-updater error:', err);
});

app.whenReady().then(() => {
  console.log('[electron] App ready, spawning sidecar...');
  spawnSidecar();
  createWindow();
  
  if (!isDev) {
    console.log('[electron] Checking for updates...');
    autoUpdater.checkForUpdatesAndNotify();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('before-quit', () => {
  console.log('[electron] App quitting, shutting down sidecar...');
  shutdownSidecar();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});