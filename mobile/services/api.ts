import { Comment } from "@/types/comment";
import { Post } from "@/types/post";
import type { AuthenticatedFetch } from "@/hooks/useAuthenticatedApi";

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
export async function getPosts(authenticatedFetch: AuthenticatedFetch): Promise<Post[]> {
    const response = await authenticatedFetch(`${API_BASE_URL}/posts`);

    if (!response.ok) {
        throw new Error('Failed to fetch posts');
    }

    return response.json();
}

export async function createPost(authenticatedFetch: AuthenticatedFetch, data: PostCreation ): Promise<Post> {
    const response = await authenticatedFetch(`${API_BASE_URL}/posts`,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    }
);

    if (!response.ok){
        throw new Error('Failed to create post')
    }
    return response.json()
}

export async function deleteUserPost(postId: number, authenticatedFetch: AuthenticatedFetch): Promise<boolean> {
    const response = await authenticatedFetch(`${API_BASE_URL}/posts/${postId}`, {
        method: 'DELETE',
    });

    if (!response.ok){
        throw new Error('Failed to remove post')
    }

    return response.json();
}

export async function likePost(postId: number, authenticatedFetch: AuthenticatedFetch): Promise<LikeStatus> {
    const response = await authenticatedFetch(`${API_BASE_URL}/posts/${postId}/like`,{
        method: 'POST',
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

export async function createPostComment(postId: number, authenticatedFetch: AuthenticatedFetch, content: string): Promise<Comment> {
    const response = await authenticatedFetch(`${API_BASE_URL}/posts/${postId}/comments`,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
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

export async function removePostComment(postId: number, commentId: number, authenticatedFetch: AuthenticatedFetch): Promise<boolean> {
    const response = await authenticatedFetch(`${API_BASE_URL}/posts/${postId}/comments/${commentId}`, {
        method: 'DELETE',
    });

    if (!response.ok){
        throw new Error('Failed to remove comment')
    }

    return response.json();
}