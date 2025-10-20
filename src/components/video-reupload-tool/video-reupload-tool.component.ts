import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface VideoSource {
  id: string;
  name: string;
  icon: string;
  color: string;
  supported: boolean;
}

interface VideoFile {
  id: string;
  name: string;
  url: string;
  size: number;
  duration: number;
  thumbnail: string;
  platform: string;
  uploadDate: Date;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
}

interface ReuploadTask {
  id: string;
  videoId: string;
  platforms: string[];
  settings: any;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  startTime?: Date;
  endTime?: Date;
  results: any[];
}

@Component({
  selector: 'app-video-reupload-tool',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './video-reupload-tool.component.html',
  styleUrls: ['./video-reupload-tool.component.css']
})
export class VideoReuploadToolComponent implements OnInit {
  // Video sources
  videoSources: VideoSource[] = [
    { id: 'tiktok', name: 'TikTok', icon: '🎵', color: '#000000', supported: true },
    { id: 'youtube', name: 'YouTube', icon: '📺', color: '#FF0000', supported: true },
    { id: 'instagram', name: 'Instagram', icon: '📷', color: '#E4405F', supported: true },
    { id: 'facebook', name: 'Facebook', icon: '👥', color: '#1877F2', supported: false },
    { id: 'twitter', name: 'Twitter', icon: '🐦', color: '#1DA1F2', supported: false }
  ];

  // Video files
  videoFiles: VideoFile[] = [];
  selectedVideos: string[] = [];

  // Reupload tasks
  reuploadTasks: ReuploadTask[] = [];
  activeTask: ReuploadTask | null = null;

  // Settings
  settings = {
    autoDownload: true,
    autoProcess: true,
    quality: 'high',
    addWatermark: false,
    watermarkText: '',
    cropVideo: false,
    resizeVideo: false,
    targetResolution: '1080x1920',
    scheduleUpload: false,
    uploadTime: '',
    retryFailed: true,
    maxRetries: 3
  };

  // UI State
  currentStep = 1;
  isProcessing = false;
  showAdvancedSettings = false;

  // Statistics
  stats = {
    totalVideos: 0,
    processedVideos: 0,
    successfulUploads: 0,
    failedUploads: 0,
    totalViews: 0,
    totalLikes: 0
  };

  constructor() { }

  ngOnInit(): void {
    this.loadVideoFiles();
    this.loadSettings();
    this.updateStats();
  }

  // Video Management
  loadVideoFiles(): void {
    // Load from localStorage or API
    const saved = localStorage.getItem('videoFiles');
    if (saved) {
      this.videoFiles = JSON.parse(saved);
    }
  }

  saveVideoFiles(): void {
    localStorage.setItem('videoFiles', JSON.stringify(this.videoFiles));
  }

  addVideoFile(file: File): void {
    const videoFile: VideoFile = {
      id: this.generateId(),
      name: file.name,
      url: URL.createObjectURL(file),
      size: file.size,
      duration: 0, // Will be calculated
      thumbnail: '',
      platform: 'local',
      uploadDate: new Date(),
      status: 'pending',
      progress: 0
    };

    this.videoFiles.push(videoFile);
    this.saveVideoFiles();
    this.updateStats();
  }

  removeVideoFile(id: string): void {
    this.videoFiles = this.videoFiles.filter(v => v.id !== id);
    this.selectedVideos = this.selectedVideos.filter(v => v !== id);
    this.saveVideoFiles();
    this.updateStats();
  }

  toggleVideoSelection(id: string): void {
    const index = this.selectedVideos.indexOf(id);
    if (index > -1) {
      this.selectedVideos.splice(index, 1);
    } else {
      this.selectedVideos.push(id);
    }
  }

  selectAllVideos(): void {
    this.selectedVideos = this.videoFiles.map(v => v.id);
  }

  clearSelection(): void {
    this.selectedVideos = [];
  }

  // Video Processing
  async processVideo(videoId: string): Promise<void> {
    const video = this.videoFiles.find(v => v.id === videoId);
    if (!video) return;

    video.status = 'processing';
    video.progress = 0;

    try {
      // Simulate video processing
      for (let i = 0; i <= 100; i += 10) {
        video.progress = i;
        await this.delay(200);
      }

      video.status = 'completed';
      this.updateStats();
    } catch (error) {
      video.status = 'failed';
      console.error('Error processing video:', error);
    }
  }

  // Reupload Management
  createReuploadTask(): void {
    if (this.selectedVideos.length === 0) {
      alert('Vui lòng chọn ít nhất một video');
      return;
    }

    const platforms = this.videoSources.filter(s => s.supported).map(s => s.id);
    
    for (const videoId of this.selectedVideos) {
      const task: ReuploadTask = {
        id: this.generateId(),
        videoId,
        platforms,
        settings: { ...this.settings },
        status: 'pending',
        progress: 0,
        results: []
      };

      this.reuploadTasks.push(task);
    }

    this.startReuploadProcess();
  }

  async startReuploadProcess(): void {
    this.isProcessing = true;
    this.currentStep = 2;

    for (const task of this.reuploadTasks.filter(t => t.status === 'pending')) {
      await this.executeReuploadTask(task);
    }

    this.isProcessing = false;
    this.currentStep = 3;
  }

  async executeReuploadTask(task: ReuploadTask): Promise<void> {
    task.status = 'running';
    task.startTime = new Date();
    this.activeTask = task;

    try {
      // Process video first
      await this.processVideo(task.videoId);

      // Upload to each platform
      for (const platform of task.platforms) {
        await this.uploadToPlatform(task, platform);
      }

      task.status = 'completed';
      task.endTime = new Date();
      this.updateStats();
    } catch (error) {
      task.status = 'failed';
      console.error('Error executing reupload task:', error);
    }

    this.activeTask = null;
  }

  async uploadToPlatform(task: ReuploadTask, platform: string): Promise<void> {
    // Simulate upload process
    for (let i = 0; i <= 100; i += 20) {
      task.progress = i;
      await this.delay(500);
    }

    const result = {
      platform,
      success: true,
      url: `https://${platform}.com/video/${this.generateId()}`,
      views: Math.floor(Math.random() * 10000),
      likes: Math.floor(Math.random() * 1000)
    };

    task.results.push(result);
  }

  // Settings Management
  loadSettings(): void {
    const saved = localStorage.getItem('reuploadSettings');
    if (saved) {
      this.settings = { ...this.settings, ...JSON.parse(saved) };
    }
  }

  saveSettings(): void {
    localStorage.setItem('reuploadSettings', JSON.stringify(this.settings));
  }

  // Utility Functions
  generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  updateStats(): void {
    this.stats.totalVideos = this.videoFiles.length;
    this.stats.processedVideos = this.videoFiles.filter(v => v.status === 'completed').length;
    this.stats.successfulUploads = this.reuploadTasks.filter(t => t.status === 'completed').length;
    this.stats.failedUploads = this.reuploadTasks.filter(t => t.status === 'failed').length;
    
    let totalViews = 0;
    let totalLikes = 0;
    
    this.reuploadTasks.forEach(task => {
      task.results.forEach(result => {
        totalViews += result.views || 0;
        totalLikes += result.likes || 0;
      });
    });
    
    this.stats.totalViews = totalViews;
    this.stats.totalLikes = totalLikes;
  }

  // UI Navigation
  nextStep(): void {
    if (this.currentStep < 3) {
      this.currentStep++;
    }
  }

  prevStep(): void {
    if (this.currentStep > 1) {
      this.currentStep--;
    }
  }

  resetTool(): void {
    this.currentStep = 1;
    this.selectedVideos = [];
    this.isProcessing = false;
    this.activeTask = null;
  }

  // File Upload
  onFileSelected(event: any): void {
    const files = event.target.files;
    for (let i = 0; i < files.length; i++) {
      this.addVideoFile(files[i]);
    }
  }

  // Format helpers
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'completed': return 'text-green-500';
      case 'processing': return 'text-blue-500';
      case 'failed': return 'text-red-500';
      default: return 'text-gray-500';
    }
  }

  getStatusIcon(status: string): string {
    switch (status) {
      case 'completed': return '✅';
      case 'processing': return '⏳';
      case 'failed': return '❌';
      default: return '⏸️';
    }
  }
}