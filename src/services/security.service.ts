
import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class SecurityService {
  isBanned = signal(false);
  isIncognito = signal(false);
  banTimeRemaining = signal(0);

  private banDuration = 5 * 60 * 1000; // 5 minutes in milliseconds
  private banCheckInterval: any;
  private readonly banStorageKey = 'user_ban_expiry';

  init() {
    this.detectIncognito();
    this.checkBanStatus();
    window.addEventListener('contextmenu', this.handleEvent);
    window.addEventListener('keydown', this.handleEvent);
  }
  
  private async detectIncognito(): Promise<void> {
    // A reliable cross-browser check for private mode.
    // It checks storage quota, which is significantly lower in private mode,
    // or catches errors thrown when trying to access storage APIs.
    if ('storage' in navigator && 'estimate' in navigator.storage) {
        try {
            const { quota } = await navigator.storage.estimate();
            // Standard quota is usually in gigabytes, incognito is often < 150MB.
            if (quota && quota < 150 * 1024 * 1024) {
                this.isIncognito.set(true);
            }
        } catch (e) {
            // Firefox throws a TypeError in private browsing when estimating.
            this.isIncognito.set(true);
        }
    } else {
        // Fallback for older browsers
        try {
            const db = window.indexedDB.open('__incognito_test__');
            db.onerror = () => this.isIncognito.set(true);
            // We don't care about success, only failure.
        } catch (e) {
             this.isIncognito.set(true);
        }
    }
  }

  private handleEvent = (e: Event) => {
    let triggered = false;
    if (e.type === 'contextmenu') {
      triggered = true;
    }
    if (e instanceof KeyboardEvent) {
      if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && ['I', 'J', 'C'].includes(e.key.toUpperCase()))) {
        triggered = true;
      }
    }

    if (triggered) {
      e.preventDefault();
      this.triggerBan();
    }
  };

  private triggerBan() {
    const expiryTime = Date.now() + this.banDuration;
    localStorage.setItem(this.banStorageKey, expiryTime.toString());
    this.isBanned.set(true);
    this.updateBanTime(expiryTime);
    this.startBanChecker();
  }

  private checkBanStatus() {
    const expiryTimeStr = localStorage.getItem(this.banStorageKey);
    if (expiryTimeStr) {
      const expiryTime = parseInt(expiryTimeStr, 10);
      if (Date.now() < expiryTime) {
        this.isBanned.set(true);
        this.updateBanTime(expiryTime);
        this.startBanChecker();
      } else {
        this.clearBan();
      }
    }
  }

  private updateBanTime(expiryTime: number) {
    const remaining = Math.max(0, expiryTime - Date.now());
    this.banTimeRemaining.set(remaining);
  }
  
  private startBanChecker() {
    if(this.banCheckInterval) return;

    this.banCheckInterval = setInterval(() => {
      const expiryTimeStr = localStorage.getItem(this.banStorageKey);
      if(expiryTimeStr) {
        const expiryTime = parseInt(expiryTimeStr, 10);
        if(Date.now() < expiryTime) {
          this.updateBanTime(expiryTime);
        } else {
          this.clearBan();
        }
      } else {
        this.clearBan();
      }
    }, 1000);
  }

  private clearBan() {
    this.isBanned.set(false);
    this.banTimeRemaining.set(0);
    localStorage.removeItem(this.banStorageKey);
    clearInterval(this.banCheckInterval);
    this.banCheckInterval = null;
  }
}
