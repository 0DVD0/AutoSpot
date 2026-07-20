export type User = {
    id: number
    username: string
    email: string
    bio: string | null
    avatar_url: string | null
    created_at: string
}

export type UserProfile = User & {
    followers_count: number;
    following_count: number;
    groups_count: number;
    active_posts_count: number;
    is_followed_by_me: boolean;
}