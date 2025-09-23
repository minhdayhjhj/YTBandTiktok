
export interface VideoInfo {
  videoId: string;
  title: string;
  publishedAt: string;
  duration: string;
  channel: {
    name: string;
    avatar: string;
    subscribers: number;
  };
  stats: {
    views: number;
    likes: number;
    comments: number;
    shares: number; // Estimated
  };
}
