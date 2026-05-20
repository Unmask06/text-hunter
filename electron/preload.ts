import { contextBridge, ipcRenderer } from 'electron';

export type UpdateInfo = {
  version: string;
  releaseDate: string;
  releaseName?: string;
};

export type ProgressInfo = {
  percent: number;
  transferred: number;
  total: number;
  bytesPerSecond: number;
};

const electronAPI = {
  isElectron: true,
  
  startSidecar: (): Promise<string> => {
    return ipcRenderer.invoke('sidecar:start');
  },
  
  shutdownSidecar: (): Promise<string> => {
    return ipcRenderer.invoke('sidecar:shutdown');
  },
  
  toggleFullscreen: (): Promise<void> => {
    return ipcRenderer.invoke('window:toggleFullscreen');
  },
  
  getVersion: (): Promise<string> => {
    return ipcRenderer.invoke('app:getVersion');
  },
  
  isPackaged: (): Promise<boolean> => {
    return ipcRenderer.invoke('app:isPackaged');
  },
  
  onUpdateAvailable: (callback: (info: UpdateInfo) => void): () => void => {
    const handler = (_event: Electron.IpcRendererEvent, info: UpdateInfo) => callback(info);
    ipcRenderer.on('update:available', handler);
    return () => ipcRenderer.removeListener('update:available', handler);
  },
  
  onUpdateProgress: (callback: (progress: ProgressInfo) => void): () => void => {
    const handler = (_event: Electron.IpcRendererEvent, progress: ProgressInfo) => callback(progress);
    ipcRenderer.on('update:progress', handler);
    return () => ipcRenderer.removeListener('update:progress', handler);
  },
  
  onUpdateDownloaded: (callback: (info: UpdateInfo) => void): () => void => {
    const handler = (_event: Electron.IpcRendererEvent, info: UpdateInfo) => callback(info);
    ipcRenderer.on('update:downloaded', handler);
    return () => ipcRenderer.removeListener('update:downloaded', handler);
  },
  
  quitAndInstall: (): void => {
    ipcRenderer.send('update:quitAndInstall');
  },
};

contextBridge.exposeInMainWorld('electronAPI', electronAPI);

export type ElectronAPI = typeof electronAPI;