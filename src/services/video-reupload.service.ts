import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';

export interface VideoMetadata {
  id: string;
  title: string;
  description: string;
  tags: string[];
  category: string;
  privacy: 'public' | 'private' | 'unlisted';
  thumbnail?: string;
  duration: number;
  resolution: string;
  fileSize: number;
}

export interface PlatformConfig {
  name: string;
  apiEndpoint: string;
  requiredFields: string[];
  maxFileSize: number;
  supportedFormats: string[];
  uploadLimits: {
    daily: number;
    hourly: number;
  };
}

export interface UploadResult {
  platform: string;
  success: boolean;
  videoId?: string;
  url?: string;
  error?: string;
  views?: number;
  likes?: number;
  shares?: number;
  comments?: number;
  uploadTime: Date;
}

@Injectable({
  providedIn: 'root'
})
export class VideoReuploadService {
  private platforms: PlatformConfig[] = [
    {
      name: 'TikTok',
      apiEndpoint: '/api/tiktok/upload',
      requiredFields: ['title', 'description', 'tags'],
      maxFileSize: 500 * 1024 * 1024, // 500MB
      supportedFormats: ['mp4', 'mov', 'avi'],
      uploadLimits: { daily: 10, hourly: 3 }
    },
    {
      name: 'YouTube',
      apiEndpoint: '/api/youtube/upload',
      requiredFields: ['title', 'description', 'category'],
      maxFileSize: 2 * 1024 * 1024 * 1024, // 2GB
      supportedFormats: ['mp4', 'mov', 'avi', 'wmv', 'flv'],
      uploadLimits: { daily: 6, hourly: 2 }
    },
    {
      name: 'Instagram',
      apiEndpoint: '/api/instagram/upload',
      requiredFields: ['title', 'description'],
      maxFileSize: 100 * 1024 * 1024, // 100MB
      supportedFormats: ['mp4', 'mov'],
      uploadLimits: { daily: 25, hourly: 5 }
    }
  ];

  private uploadQueue: BehaviorSubject<any[]> = new BehaviorSubject([]);
  private uploadHistory: BehaviorSubject<UploadResult[]> = new BehaviorSubject([]);

  constructor(private http: HttpClient) { }

  // Platform Management
  getSupportedPlatforms(): PlatformConfig[] {
    return this.platforms;
  }

  getPlatformConfig(platformName: string): PlatformConfig | undefined {
    return this.platforms.find(p => p.name.toLowerCase() === platformName.toLowerCase());
  }

  // Video Processing
  async processVideo(file: File, settings: any): Promise<VideoMetadata> {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      video.preload = 'metadata';
      
      video.onloadedmetadata = () => {
        const metadata: VideoMetadata = {
          id: this.generateId(),
          title: file.name.replace(/\.[^/.]+$/, ''),
          description: '',
          tags: [],
          category: 'Entertainment',
          privacy: 'public',
          duration: video.duration,
          resolution: `${video.videoWidth}x${video.videoHeight}`,
          fileSize: file.size
        };
        resolve(metadata);
      };

      video.onerror = () => {
        reject(new Error('Failed to load video metadata'));
      };

      video.src = URL.createObjectURL(file);
    });
  }

  // Video Editing
  async cropVideo(file: File, cropSettings: any): Promise<File> {
    return new Promise((resolve, reject) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const video = document.createElement('video');

      video.onloadedmetadata = () => {
        canvas.width = cropSettings.width || video.videoWidth;
        canvas.height = cropSettings.height || video.videoHeight;

        video.currentTime = cropSettings.startTime || 0;
        video.onseeked = () => {
          if (ctx) {
            ctx.drawImage(video, 
              cropSettings.x || 0, 
              cropSettings.y || 0, 
              cropSettings.width || video.videoWidth, 
              cropSettings.height || video.videoHeight,
              0, 0, canvas.width, canvas.height
            );
          }

          canvas.toBlob((blob) => {
            if (blob) {
              const croppedFile = new File([blob], file.name, { type: file.type });
              resolve(croppedFile);
            } else {
              reject(new Error('Failed to crop video'));
            }
          }, file.type);
        };
      };

      video.src = URL.createObjectURL(file);
    });
  }

  async resizeVideo(file: File, targetResolution: string): Promise<File> {
    return new Promise((resolve, reject) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const video = document.createElement('video');

      const [width, height] = targetResolution.split('x').map(Number);

      video.onloadedmetadata = () => {
        canvas.width = width;
        canvas.height = height;

        video.onseeked = () => {
          if (ctx) {
            ctx.drawImage(video, 0, 0, width, height);
          }

          canvas.toBlob((blob) => {
            if (blob) {
              const resizedFile = new File([blob], file.name, { type: file.type });
              resolve(resizedFile);
            } else {
              reject(new Error('Failed to resize video'));
            }
          }, file.type);
        };

        video.currentTime = 0;
      };

      video.src = URL.createObjectURL(file);
    });
  }

  async addWatermark(file: File, watermarkText: string): Promise<File> {
    return new Promise((resolve, reject) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const video = document.createElement('video');

      video.onloadedmetadata = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        video.onseeked = () => {
          if (ctx) {
            ctx.drawImage(video, 0, 0);
            
            // Add watermark
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.font = '24px Arial';
            ctx.textAlign = 'right';
            ctx.fillText(watermarkText, canvas.width - 20, canvas.height - 20);
          }

          canvas.toBlob((blob) => {
            if (blob) {
              const watermarkedFile = new File([blob], file.name, { type: file.type });
              resolve(watermarkedFile);
            } else {
              reject(new Error('Failed to add watermark'));
            }
          }, file.type);
        };

        video.currentTime = 0;
      };

      video.src = URL.createObjectURL(file);
    });
  }

  // Upload Management
  async uploadToPlatform(file: File, platform: string, metadata: VideoMetadata): Promise<UploadResult> {
    const platformConfig = this.getPlatformConfig(platform);
    if (!platformConfig) {
      throw new Error(`Unsupported platform: ${platform}`);
    }

    // Check file size
    if (file.size > platformConfig.maxFileSize) {
      throw new Error(`File too large for ${platform}. Max size: ${this.formatFileSize(platformConfig.maxFileSize)}`);
    }

    // Check upload limits
    if (!this.canUpload(platform)) {
      throw new Error(`Upload limit reached for ${platform}`);
    }

    try {
      const formData = new FormData();
      formData.append('video', file);
      formData.append('metadata', JSON.stringify(metadata));

      const response = await this.http.post<any>(platformConfig.apiEndpoint, formData).toPromise();
      
      const result: UploadResult = {
        platform,
        success: true,
        videoId: response.videoId,
        url: response.url,
        views: response.views || 0,
        likes: response.likes || 0,
        shares: response.shares || 0,
        comments: response.comments || 0,
        uploadTime: new Date()
      };

      this.addToHistory(result);
      this.updateUploadLimits(platform);
      
      return result;
    } catch (error) {
      const result: UploadResult = {
        platform,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        uploadTime: new Date()
      };

      this.addToHistory(result);
      throw error;
    }
  }

  async batchUpload(files: File[], platforms: string[], metadata: VideoMetadata): Promise<UploadResult[]> {
    const results: UploadResult[] = [];
    
    for (const file of files) {
      for (const platform of platforms) {
        try {
          const result = await this.uploadToPlatform(file, platform, metadata);
          results.push(result);
        } catch (error) {
          console.error(`Failed to upload ${file.name} to ${platform}:`, error);
          results.push({
            platform,
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error',
            uploadTime: new Date()
          });
        }
      }
    }

    return results;
  }

  // Schedule Management
  scheduleUpload(file: File, platforms: string[], metadata: VideoMetadata, scheduleTime: Date): void {
    const now = new Date();
    const delay = scheduleTime.getTime() - now.getTime();

    if (delay > 0) {
      setTimeout(async () => {
        try {
          await this.batchUpload([file], platforms, metadata);
        } catch (error) {
          console.error('Scheduled upload failed:', error);
        }
      }, delay);
    }
  }

  // Analytics
  getUploadHistory(): Observable<UploadResult[]> {
    return this.uploadHistory.asObservable();
  }

  getUploadStats(): any {
    const history = this.uploadHistory.value;
    const totalUploads = history.length;
    const successfulUploads = history.filter(r => r.success).length;
    const totalViews = history.reduce((sum, r) => sum + (r.views || 0), 0);
    const totalLikes = history.reduce((sum, r) => sum + (r.likes || 0), 0);
    const totalShares = history.reduce((sum, r) => sum + (r.shares || 0), 0);

    return {
      totalUploads,
      successfulUploads,
      failedUploads: totalUploads - successfulUploads,
      successRate: totalUploads > 0 ? (successfulUploads / totalUploads) * 100 : 0,
      totalViews,
      totalLikes,
      totalShares,
      averageViews: successfulUploads > 0 ? totalViews / successfulUploads : 0
    };
  }

  // Utility Functions
  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  private formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  private canUpload(platform: string): boolean {
    const limits = this.getPlatformConfig(platform)?.uploadLimits;
    if (!limits) return true;

    const today = new Date().toDateString();
    const thisHour = new Date().getHours();
    
    const todayUploads = this.uploadHistory.value.filter(r => 
      r.platform === platform && 
      r.uploadTime.toDateString() === today
    ).length;

    const hourUploads = this.uploadHistory.value.filter(r => 
      r.platform === platform && 
      r.uploadTime.getHours() === thisHour
    ).length;

    return todayUploads < limits.daily && hourUploads < limits.hourly;
  }

  private updateUploadLimits(platform: string): void {
    // This would typically update a database or cache
    // For now, we'll just log it
    console.log(`Upload completed for ${platform}`);
  }

  private addToHistory(result: UploadResult): void {
    const current = this.uploadHistory.value;
    this.uploadHistory.next([...current, result]);
  }

  // Download Management
  async downloadVideo(url: string, platform: string): Promise<File> {
    try {
      const response = await this.http.get(url, { responseType: 'blob' }).toPromise();
      const file = new File([response], `downloaded_${platform}_${Date.now()}.mp4`, { type: 'video/mp4' });
      return file;
    } catch (error) {
      throw new Error(`Failed to download video from ${platform}: ${error}`);
    }
  }

  // Bulk Operations
  async bulkDownload(urls: string[], platform: string): Promise<File[]> {
    const files: File[] = [];
    
    for (const url of urls) {
      try {
        const file = await this.downloadVideo(url, platform);
        files.push(file);
      } catch (error) {
        console.error(`Failed to download ${url}:`, error);
      }
    }

    return files;
  }

  // Cleanup
  clearHistory(): void {
    this.uploadHistory.next([]);
  }

  clearQueue(): void {
    this.uploadQueue.next([]);
  }
}