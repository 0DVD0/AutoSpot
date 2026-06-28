import { Comment } from "@/types/comment";
import { Post } from "@/types/post";

export const API_BASE_URL = 'http://192.168.100.11:8000';

type PostCreation = {
    image_url: string;
    brand: string | null;
    model: string | null;
    ai_confidence?: number | null;
    latitude: number | null;
    longitude: number | null;
    location_visibility: string;
};

type LikeStatus = {
    post_id: number;
    likes_count: number;
    is_liked_by_me: boolean;
}
export async function getPosts(token: string) {
    const response = await fetch(`${API_BASE_URL}/posts`, {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    if (!response.ok) {
        throw new Error('Failed to fetch posts');
    }

    return response.json();
}

export async function createPost(token: string, data: PostCreation ): Promise<Post> {
    const response = await fetch(`${API_BASE_URL}/posts`,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(data),
    }
);

    if (!response.ok){
        throw new Error('Failed to create post')
    }
    return response.json()
}

export async function deleteUserPost(postId: number, token: string): Promise<boolean> {
    const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
        method: 'DELETE',
        headers: {
            Authorization: `Bearer ${token}`,
        }
    });

    if (!response.ok){
        throw new Error('Failed to remove post')
    }

    return response.json();
}

export async function likePost(postId: number, token: string): Promise<LikeStatus> {
    const response = await fetch(`${API_BASE_URL}/posts/${postId}/like`,{
        method: 'POST',
        headers: {
            Authorization: `Bearer ${token}` 
        }
    }
    )

    if (!response.ok){
        throw new Error('Failed to like the post')
    }
    return response.json()
}

export async function getPostComments(postId: number): Promise<Comment[]> {
     const response = await fetch(`${API_BASE_URL}/posts/${postId}/comments`);

    if (!response.ok) {
        throw new Error('Failed to fetch comments');
    }

    return response.json();
}

export async function createPostComment(postId: number, token: string, content: string): Promise<Comment> {
    const response = await fetch(`${API_BASE_URL}/posts/${postId}/comments`,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        },
        
        body: JSON.stringify({
            content: content
        }),
    }
);

    if (!response.ok){
        throw new Error('Failed to create comment')
    }
    return response.json()
}