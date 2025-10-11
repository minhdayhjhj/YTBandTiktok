
import { inject, Injectable, signal } from '@angular/core';
import { HttpClient, HttpEventType, HttpProgressEvent } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { TiktokVideoInfo, TikWmApiResponse, DownloadProgress, VideoQuality } from '../models/tiktok.model';

@Injectable({ providedIn: 'root' })
export class TiktokDataService {
  private http = inject(HttpClient);
  private apiUrl = 'https://www.tikwm.com/api/';
  
  // Signals for download state management
  downloadProgress = signal<DownloadProgress | null>(null);
  isDownloading = signal(false);
  downloadHistory = signal<Array<{id: string, video: TiktokVideoInfo, downloadedAt: Date, fileSize?: number}>>([]);

  async getVideoInfo(videoUrl: string): Promise<TiktokVideoInfo> {
    try {
      const url = `${this.apiUrl}?url=${encodeURIComponent(videoUrl)}`;
      const response = await firstValueFrom(this.http.get<TikWmApiResponse>(url));

      if (response.code !== 0 || !response.data) {
        throw new Error(response.msg || 'Invalid response from TikTok API.');
      }

      const data = response.data;
      return {
        title: data.title,
        create_time: data.create_time,
        duration: data.duration,
        videoUrl: data.play,
        author: {
          avatar: data.author.avatar,
          unique_id: data.author.unique_id,
          nickname: data.author.nickname,
        },
        stats: {
          play_count: data.play_count,
          digg_count: data.digg_count,
          share_count: data.share_count,
          comment_count: data.comment_count,
          download_count: data.download_count,
        }
      };
    } catch (error) {
      console.error('TikTok API Error:', error);
      throw new Error('Could not fetch data for this TikTok video.');
    }
  }

  async downloadVideo(videoInfo: TiktokVideoInfo, quality: VideoQuality = 'high'): Promise<void> {
    this.isDownloading.set(true);
    this.downloadProgress.set({ percentage: 0, loaded: 0, total: 0 });

    try {
      // Create a unique ID for this download
      const downloadId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      
      // Start download with progress tracking
      const response = await firstValueFrom(
        this.http.get(videoInfo.videoUrl, {
          responseType: 'blob',
          reportProgress: true,
          observe: 'events'
        })
      );

      if (response.type === HttpEventType.DownloadProgress) {
        const progress = response as HttpProgressEvent;
        if (progress.total) {
          const percentage = Math.round((100 * progress.loaded) / progress.total);
          this.downloadProgress.set({
            percentage,
            loaded: progress.loaded,
            total: progress.total
          });
        }
      } else if (response.type === HttpEventType.Response) {
        const blob = response.body;
        if (blob) {
          // Create download link
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          
          // Generate filename
          const sanitizedTitle = videoInfo.title.replace(/[^a-zA-Z0-9\s]/g, '').substring(0, 50);
          const timestamp = new Date(videoInfo.create_time * 1000).toISOString().split('T')[0];
          link.download = `tiktok_${sanitizedTitle}_${timestamp}.mp4`;
          
          // Trigger download
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);

          // Add to download history
          const historyItem = {
            id: downloadId,
            video: videoInfo,
            downloadedAt: new Date(),
            fileSize: blob.size
          };
          this.downloadHistory.update(history => [...history, historyItem]);

          // Reset progress
          this.downloadProgress.set(null);
        }
      }
    } catch (error) {
      console.error('Download error:', error);
      throw new Error('Failed to download video. Please try again.');
    } finally {
      this.isDownloading.set(false);
    }
  }

  clearDownloadHistory(): void {
    this.downloadHistory.set([]);
  }

  removeFromHistory(downloadId: string): void {
    this.downloadHistory.update(history => 
      history.filter(item => item.id !== downloadId)
    );
  }
}
