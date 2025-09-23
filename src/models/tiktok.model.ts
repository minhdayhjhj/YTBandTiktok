
export interface TiktokVideoInfo {
  title: string;
  create_time: number; // timestamp
  duration: number; // seconds
  videoUrl: string;
  author: {
    avatar: string;
    unique_id: string;
    nickname: string;
  };
  stats: {
    play_count: number;
    digg_count: number; // likes
    share_count: number;
    comment_count: number;
    download_count: number;
  };
}

// Raw API response structure for type assertion
export interface TikWmApiResponse {
  code: number;
  msg: string;
  data: {
    title: string;
    create_time: number;
    duration: number;
    play: string; // video url
    author: {
      avatar: string;
      unique_id: string;
      nickname: string;
    };
    play_count: number;
    digg_count: number;
    share_count: number;
    comment_count: number;
    download_count: number;
  };
}
