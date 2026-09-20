const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('galaxyAPI', {
    getSystemInfo: () => ({ platform: process.platform, arch: process.arch })
});
