import { Component, OnInit, inject, signal, computed, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
// Fix: Correctly import GoogleGenAI
import { GoogleGenAI, GenerateContentResponse } from '@google/genai';

import { YoutubeDataService } from './services/youtube-data.service';
import { TiktokDataService } from './services/tiktok-data.service';
import { SecurityService } from './services/security.service';
import { AudioService } from './services/audio.service';

import { VideoInfo } from './models/youtube.model';
import { TiktokVideoInfo, VideoQuality } from './models/tiktok.model';

import { EffectsComponent } from './components/effects/effects.component';
import { BanScreenComponent } from './components/ban-screen/ban-screen.component';

type Platform = 'youtube' | 'tiktok';
type VideoData = VideoInfo | TiktokVideoInfo;

declare const process: any; // Assume process.env is available

@Component({
  selector: 'app-root',
  template: `
    <app-effects />

    @if (isBanned()) {
      <app-ban-screen />
    } @else {
      <main class="relative z-10 flex flex-col items-center justify-center min-h-screen p-4 text-green-400 font-mono bg-black bg-opacity-50">
        <div class="absolute top-4 right-4">
          <button (click)="audioService.togglePlay()" class="px-3 py-2 border border-green-400 text-green-400 hover:bg-green-400 hover:text-black transition-colors duration-300">
            @if (audioService.isPlaying()) {
              <span>SOUND [ON]</span>
            } @else {
              <span>SOUND [OFF]</span>
            }
          </button>
        </div>
        
        <div class="w-full max-w-6xl p-6 border border-green-600 bg-black bg-opacity-70 shadow-lg shadow-green-500/20">
          <header class="text-center mb-6">
            <h1 class="text-4xl font-bold animate-flicker">TIKTOK DOWNLOADER v2.0</h1>
            <p class="text-green-300">Download TikTok videos with high quality and viral analysis...</p>
          </header>

          <section class="mb-6">
            <div class="flex space-x-2 mb-4">
              <button 
                (click)="setPlatform('youtube')" 
                class="px-4 py-2 border border-green-700 bg-gray-900 text-green-500 hover:bg-green-800 transition-colors"
                [class.bg-green-600]="platform() === 'youtube'"
                [class.text-black]="platform() === 'youtube'"
                [class.border-green-400]="platform() === 'youtube'"
                [class.font-bold]="platform() === 'youtube'">
                > YouTube
              </button>
              <button 
                (click)="setPlatform('tiktok')" 
                class="px-4 py-2 border border-green-700 bg-gray-900 text-green-500 hover:bg-green-800 transition-colors"
                [class.bg-green-600]="platform() === 'tiktok'"
                [class.text-black]="platform() === 'tiktok'"
                [class.border-green-400]="platform() === 'tiktok'"
                [class.font-bold]="platform() === 'tiktok'">
                > TikTok
              </button>
              <button 
                (click)="toggleDownloadHistory()" 
                class="px-4 py-2 border border-blue-700 bg-gray-900 text-blue-500 hover:bg-blue-800 transition-colors">
                > Download History
              </button>
            </div>
            <div class="flex">
              <input 
                type="text"
                [(ngModel)]="videoUrl"
                (keyup.enter)="analyze()"
                [placeholder]="'Paste ' + platform() + ' video URL here...'"
                class="flex-grow p-3 bg-gray-900 border border-green-500 text-green-300 focus:outline-none focus:ring-2 focus:ring-green-400 placeholder-green-700">
              <button
                (click)="analyze()"
                [disabled]="isLoading() || !isValidUrl()"
                class="px-6 py-3 bg-green-700 text-black font-bold border border-green-500 hover:bg-green-500 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors">
                ANALYZE
              </button>
            </div>
          </section>
          
          <section class="min-h-[400px] p-4 border border-dashed border-green-800 bg-black">
            @if (isLoading()) {
              <div class="flex flex-col items-center justify-center h-full">
                <div class="border-4 border-green-900 border-t-green-400 rounded-full w-12 h-12 animate-spin"></div>
                <p class="mt-4 text-lg animate-pulse">Scanning digital signatures... please wait.</p>
              </div>
            } @else if (error()) {
              <div class="text-red-500 text-center p-4">
                <h3 class="text-2xl font-bold mb-2">!! ANALYSIS FAILED !!</h3>
                <p>{{ error() }}</p>
              </div>
            } @else if (analysis()) {
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="md:col-span-1 space-y-3">
                  <h3 class="text-xl font-bold border-b border-green-700 pb-1">Video Metadata</h3>
                  @if (videoData(); as data) {
                    @if (platform() === 'youtube' && 'videoId' in data) {
                      @let video = data;
                      <p><strong>Title:</strong> {{ video.title }}</p>
                      <p><strong>Channel:</strong> {{ video.channel.name }}</p>
                      <p><strong>Subs:</strong> {{ formatNumber(video.channel.subscribers) }}</p>
                      <p><strong>Views:</strong> {{ formatNumber(video.stats.views) }}</p>
                      <p><strong>Likes:</strong> {{ formatNumber(video.stats.likes) }}</p>
                    }
                    @if (platform() === 'tiktok' && 'create_time' in data) {
                      @let video = data;
                      <p><strong>Title:</strong> {{ video.title }}</p>
                      <p><strong>Creator:</strong> @{{ video.author.unique_id }}</p>
                      <p><strong>Plays:</strong> {{ formatNumber(video.stats.play_count) }}</p>
                      <p><strong>Likes:</strong> {{ formatNumber(video.stats.digg_count) }}</p>
                      <p><strong>Shares:</strong> {{ formatNumber(video.stats.share_count) }}</p>
                    }
                  }
                </div>
                <div class="md:col-span-2">
                  <h3 class="text-xl font-bold border-b border-green-700 pb-1">Gemini Viral Analysis</h3>
                  <pre class="whitespace-pre-wrap font-mono text-green-300 mt-2">{{ analysis() }}</pre>
                </div>
              </div>
            } @else {
              <div class="flex items-center justify-center h-full">
                <p class="text-green-600">Awaiting input for viral analysis...</p>
              </div>
            }
          </section>
        </div>

        <footer class="mt-8 text-center text-sm text-green-700">
          <p>DISCLAIMER: This tool is for educational purposes only. Data is mocked or retrieved from public APIs.</p>
          <p>Analysis powered by Google Gemini.</p>
        </footer>
      </main>
    }
    
    <style>
      @keyframes flicker {
        0%, 100% {
          text-shadow: 0 0 2px #0f0, 0 0 5px #0f0, 0 0 10px #0f0, 0 0 20px #2f2;
          opacity: 1;
        }
        50% {
          text-shadow: none;
          opacity: 0.8;
        }
      }
      .animate-flicker {
        animation: flicker 1.5s infinite;
      }
    </style>
  `,
  standalone: true,
  imports: [CommonModule, FormsModule, EffectsComponent, BanScreenComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppComponent implements OnInit {
  private youtubeService = inject(YoutubeDataService);
  private tiktokService = inject(TiktokDataService);
  private securityService = inject(SecurityService);
  audioService = inject(AudioService);

  videoUrl = signal('');
  platform = signal<Platform>('tiktok');
  isLoading = signal(false);
  error = signal<string | null>(null);
  analysis = signal<string | null>(null);
  videoData = signal<VideoData | null>(null);
  showDownloadHistory = signal(false);
  selectedQuality = signal<VideoQuality>('high');

  isBanned = this.securityService.isBanned;

  private ai!: GoogleGenAI;
  
  isValidUrl = computed(() => {
    const url = this.videoUrl().trim();
    if (!url) return false;
    try {
      const parsedUrl = new URL(url);
      return ['youtube.com', 'www.youtube.com', 'youtu.be', 'tiktok.com', 'www.tiktok.com'].some(host => parsedUrl.hostname.includes(host));
    } catch (_) {
      return false;
    }
  });
  
  constructor() {
    if (typeof process !== 'undefined' && process.env && process.env.API_KEY) {
      // Fix: Initialize the GenAI client
      this.ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
    } else {
      console.error("API_KEY environment variable not set. Analysis will fail.");
    }
  }

  ngOnInit() {
    this.securityService.init();
    this.audioService.loadAudio('https://cdn.pixabay.com/download/audio/2022/10/22/audio_9273461461.mp3');
  }

  setPlatform(p: Platform) {
    this.platform.set(p);
  }

  async analyze() {
    if (!this.isValidUrl() || this.isLoading()) {
      if (!this.isValidUrl()) this.error.set('Please enter a valid video URL.');
      return;
    }
    
    if (!this.ai) {
        this.error.set("Cannot analyze: API key is not configured.");
        return;
    }

    this.isLoading.set(true);
    this.error.set(null);
    this.analysis.set(null);
    this.videoData.set(null);

    try {
      let data: VideoData;
      if (this.platform() === 'youtube') {
        data = await this.youtubeService.getVideoInfo(this.videoUrl());
      } else {
        data = await this.tiktokService.getVideoInfo(this.videoUrl());
      }
      this.videoData.set(data);

      const prompt = this.createPrompt(data);
      // Fix: Call the generateContent method correctly
      const result: GenerateContentResponse = await this.ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: prompt,
      });

      // Fix: Extract text from the response correctly
      this.analysis.set(result.text);

    } catch (err) {
      this.error.set(err instanceof Error ? err.message : 'An unknown error occurred during analysis.');
      console.error(err);
    } finally {
      this.isLoading.set(false);
    }
  }

  private createPrompt(data: VideoData): string {
    const isYoutube = 'videoId' in data;
    const platformName = isYoutube ? 'YouTube' : 'TikTok';
    const commonDetails = `Title: ${data.title}\nDuration: ${data.duration} seconds`;

    let statsDetails = '';
    if (isYoutube) {
      const video = data as VideoInfo;
      statsDetails = `
        Channel: ${video.channel.name} (${this.formatNumber(video.channel.subscribers)} subscribers)
        Views: ${this.formatNumber(video.stats.views)}
        Likes: ${this.formatNumber(video.stats.likes)}
        Comments: ${this.formatNumber(video.stats.comments)}
      `;
    } else {
      const video = data as TiktokVideoInfo;
       statsDetails = `
        Creator: ${video.author.nickname} (@${video.author.unique_id})
        Views (Plays): ${this.formatNumber(video.stats.play_count)}
        Likes (Diggs): ${this.formatNumber(video.stats.digg_count)}
        Comments: ${this.formatNumber(video.stats.comment_count)}
        Shares: ${this.formatNumber(video.stats.share_count)}
       `;
    }

    return `
      Analyze the viral potential of the following ${platformName} video. Provide a score out of 100 and a detailed breakdown of its strengths and weaknesses based on these stats. Be critical and specific. Format your response in markdown.

      Platform: ${platformName}
      ${commonDetails}
      ${statsDetails}
      
      Analysis:
    `;
  }

  formatNumber(num: number): string {
    return num ? num.toLocaleString('en-US') : 'N/A';
  }

  async downloadVideo() {
    const data = this.videoData();
    if (!data || this.platform() !== 'tiktok') return;
    
    try {
      await this.tiktokService.downloadVideo(data as TiktokVideoInfo, this.selectedQuality());
    } catch (error) {
      this.error.set(error instanceof Error ? error.message : 'Download failed');
    }
  }

  toggleDownloadHistory() {
    this.showDownloadHistory.update(show => !show);
  }

  setQuality(quality: VideoQuality) {
    this.selectedQuality.set(quality);
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}
