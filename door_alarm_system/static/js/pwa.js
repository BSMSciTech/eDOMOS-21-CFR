// PWA Installation and Management
class PWAManager {
    constructor() {
        this.deferredPrompt = null;
        this.isInstalled = false;
        this.init();
    }

    init() {
        // Register service worker
        if ('serviceWorker' in navigator) {
            this.registerServiceWorker();
        }

        // Handle install prompt
        this.handleInstallPrompt();
        
        // Check if already installed
        this.checkInstallation();
        
        // Setup push notifications
        this.setupPushNotifications();
    }

    async registerServiceWorker() {
        try {
            const registration = await navigator.serviceWorker.register('/static/sw.js');
            console.log('ServiceWorker registration successful:', registration.scope);
            
            // Update service worker
            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;
                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        // New content available, notify user
                        this.showUpdateNotification();
                    }
                });
            });
        } catch (error) {
            console.log('ServiceWorker registration failed:', error);
        }
    }

    handleInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('beforeinstallprompt fired');
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        window.addEventListener('appinstalled', (evt) => {
            console.log('App installed');
            this.isInstalled = true;
            this.hideInstallButton();
            this.showInstalledMessage();
        });
    }

    checkInstallation() {
        // Check if running in standalone mode (installed)
        if (window.matchMedia('(display-mode: standalone)').matches) {
            this.isInstalled = true;
            console.log('App is running in standalone mode');
        }
        
        // Manual install option disabled - no floating button needed
        /*
        // Show manual install option after a delay if auto-prompt doesn't appear
        setTimeout(() => {
            if (!this.isInstalled && !document.getElementById('pwa-install-btn')) {
                this.showManualInstallOption();
            }
        }, 5000);
        */
    }
    
    showManualInstallOption() {
        // Show manual install instructions
        const manualBtn = document.createElement('button');
        manualBtn.id = 'pwa-manual-btn';
        manualBtn.className = 'btn btn-outline-primary position-fixed';
        manualBtn.style.cssText = `
            bottom: 20px; 
            right: 20px; 
            z-index: 9999; 
            border-radius: 50px;
            padding: 12px 20px;
        `;
        manualBtn.innerHTML = '<i class="fas fa-mobile-alt me-2"></i>Mobile App';
        manualBtn.onclick = () => this.showInstallInstructions();
        document.body.appendChild(manualBtn);
    }
    
    showInstallInstructions() {
        // Create modal with install instructions
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-mobile-alt me-2"></i>Install eDOMOS App
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6><i class="fab fa-chrome me-2"></i>Chrome Browser</h6>
                                <ol class="small">
                                    <li>Tap the <strong>menu (⋮)</strong> in Chrome</li>
                                    <li>Select <strong>"Add to Home Screen"</strong></li>
                                    <li>Name it <strong>"eDOMOS"</strong></li>
                                    <li>Tap <strong>"Add"</strong></li>
                                </ol>
                            </div>
                            <div class="col-md-6">
                                <h6><i class="fab fa-firefox-browser me-2"></i>Firefox/Other</h6>
                                <ol class="small">
                                    <li>Tap <strong>browser menu</strong></li>
                                    <li>Look for <strong>"Install"</strong> or <strong>"Add to Home"</strong></li>
                                    <li>Follow the prompts</li>
                                </ol>
                            </div>
                        </div>
                        
                        <div class="alert alert-info mt-3">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Benefits:</strong> Home screen icon, offline access, push notifications, full-screen experience
                        </div>
                        
                        <div class="text-center mt-3">
                            <small class="text-muted">
                                Current URL: <code>${window.location.href}</code>
                            </small>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="window.location.reload()">
                            <i class="fas fa-sync-alt me-2"></i>Refresh Page
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        // Show the modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Remove modal after it's hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    showInstallButton() {
        // PWA install prompts disabled - just creates home screen bookmark, not real installation
        // Commented out to reduce interface clutter and misleading "install" terminology
        /*
        // Create install button if it doesn't exist
        if (!document.getElementById('pwa-install-btn')) {
            const installBtn = document.createElement('button');
            installBtn.id = 'pwa-install-btn';
            installBtn.className = 'btn btn-success btn-lg position-fixed';
            installBtn.style.cssText = `
                bottom: 20px; 
                right: 20px; 
                z-index: 9999; 
                border-radius: 50px;
                padding: 15px 25px;
                font-weight: bold;
                box-shadow: 0 4px 20px rgba(74, 144, 226, 0.5);
                animation: pulse 2s infinite;
            `;
            installBtn.innerHTML = '<i class="fas fa-download me-2"></i>Install App';
            installBtn.onclick = () => this.installApp();
            document.body.appendChild(installBtn);
            
            // Also show in navbar for better visibility
            this.showNavbarInstallPrompt();
        }
        */
    }
    
    showNavbarInstallPrompt() {
        // PWA install prompts disabled - just creates home screen bookmark, not real installation
        // Commented out to reduce interface clutter
        /*
        const navbar = document.querySelector('.navbar');
        if (navbar && !document.getElementById('navbar-install-prompt')) {
            const prompt = document.createElement('div');
            prompt.id = 'navbar-install-prompt';
            prompt.className = 'alert alert-info alert-dismissible fade show m-2';
            prompt.innerHTML = `
                <i class="fas fa-mobile-alt"></i> 
                <strong>Install eDOMOS App:</strong> Get the native app experience!
                <button class="btn btn-sm btn-success ms-2" onclick="window.pwaManager.installApp()">
                    <i class="fas fa-download"></i> Install Now
                </button>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            navbar.parentNode.insertBefore(prompt, navbar.nextSibling);
        }
        */
    }

    hideInstallButton() {
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.remove();
        }
        const navbarPrompt = document.getElementById('navbar-install-prompt');
        if (navbarPrompt) {
            navbarPrompt.remove();
        }
    }

    async installApp() {
        if (!this.deferredPrompt) {
            console.log('No install prompt available');
            return;
        }

        this.deferredPrompt.prompt();
        const { outcome } = await this.deferredPrompt.userChoice;
        
        if (outcome === 'accepted') {
            console.log('User accepted the install prompt');
        } else {
            console.log('User dismissed the install prompt');
        }
        
        this.deferredPrompt = null;
        this.hideInstallButton();
    }

    showInstalledMessage() {
        // Show success message
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show position-fixed" 
                 style="top: 20px; right: 20px; z-index: 10000;">
                <i class="fas fa-check-circle"></i> eDOMOS app installed successfully!
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.body.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    showUpdateNotification() {
        // Show update available notification
        const updateNotification = document.createElement('div');
        updateNotification.innerHTML = `
            <div class="alert alert-info alert-dismissible fade show position-fixed" 
                 style="top: 80px; right: 20px; z-index: 10000;">
                <i class="fas fa-sync-alt"></i> App update available! 
                <button class="btn btn-sm btn-outline-primary ms-2" onclick="location.reload()">
                    Update Now
                </button>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.body.appendChild(updateNotification);
    }

    async setupPushNotifications() {
        if (!('Notification' in window) || !('serviceWorker' in navigator)) {
            console.log('Push notifications not supported');
            return;
        }

        // Request permission for notifications
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            console.log('Notification permission:', permission);
        }
    }

    // Send push notification (for testing)
    sendTestNotification(message = 'eDOMOS Alert: Door status changed') {
        if (Notification.permission === 'granted') {
            new Notification('eDOMOS Alert', {
                body: message,
                icon: '/static/icons/icon-192x192.png',
                badge: '/static/icons/icon-72x72.png',
                vibrate: [100, 50, 100]
            });
        }
    }

    // Check if device is mobile
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    // Get device info for analytics
    getDeviceInfo() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            isMobile: this.isMobile(),
            isInstalled: this.isInstalled,
            isOnline: navigator.onLine,
            language: navigator.language
        };
    }
}

// Initialize PWA Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pwaManager = new PWAManager();
    
    // Add mobile-specific styles
    if (window.pwaManager.isMobile()) {
        document.body.classList.add('mobile-device');
    }
    
    // Add install status to body class
    if (window.pwaManager.isInstalled) {
        document.body.classList.add('pwa-installed');
    }
});

// Export for use in other scripts
window.PWAManager = PWAManager;