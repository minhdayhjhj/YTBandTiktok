import { Injectable } from '@angular/core';
import { VideoInfo } from '../models/youtube.model';

@Injectable({ providedIn: 'root' })
export class YoutubeDataService {
  async getVideoInfo(videoUrl: string): Promise<VideoInfo> {
    // Fix: In a real application, this would make an HTTP request to a YouTube Data API
    // or a backend service that scrapes the data. For this demo, we'll return mock data.
    console.log(`Fetching YouTube data for: ${videoUrl}`);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 800));

    // Basic URL parsing to get a video ID for more "realistic" mocking
    let videoId = 'dQw4w9WgXcQ'; // Default Rick Astley
    try {
        const url = new URL(videoUrl);
        if (url.hostname.includes('youtube.com')) {
            videoId = url.searchParams.get('v') || videoId;
        } else if (url.hostname.includes('youtu.be')) {
            videoId = url.pathname.substring(1) || videoId;
        }
    } catch (e) {
        console.warn('Invalid YouTube URL, using default mock data.');
    }
    
    // Return mock data
    return {
      videoId: videoId,
      title: 'Analyzing Viral Potential of a YouTube Video',
      publishedAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(), // Mock published 30 days ago
      duration: '212', // seconds
      channel: {
        name: 'MockChannel',
        avatar: `https://i.pravatar.cc/48?u=${videoId}`,
        subscribers: this.getRandomInt(100000, 5000000),
      },
      stats: {
        views: this.getRandomInt(1000000, 25000000),
        likes: this.getRandomInt(50000, 1000000),
        comments: this.getRandomInt(1000, 50000),
        shares: this.getRandomInt(5000, 100000),
      },
    };
  }

  private getRandomInt(min: number, max: number): number {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }
}
