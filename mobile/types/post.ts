export type Post = {
  id: number;
  user_id: number;
  image_url: string;
  brand: string | null;
  model: string | null;
  latitude: number | null;
  longitude: number | null;
  location_visibility: string;
  is_active: boolean;
  created_at: string;
  expires_at: string;
  user: PostAuthor
  likes_count: number;
  comments_count: number;
  is_liked_by_me: boolean;
};

type PostAuthor = {
  id: number;
  username: string;
  avatar_url: string | null;
};