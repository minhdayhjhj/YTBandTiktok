
import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { TiktokVideoInfo, TikWmApiResponse } from '../models/tiktok.model';

@Injectable({ providedIn: 'root' })
export class TiktokDataService {
  private http = inject(HttpClient);
  private apiUrl = 'https://www.tikwm.com/api/';

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
}
