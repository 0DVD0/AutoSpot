import type { AuthenticatedFetch } from "@/hooks/useAuthenticatedApi";
import { Post } from "@/types/post";
import { API_BASE_URL } from "./api";

export type ExploreBounds = {
    minLat: number
    maxLat: number
    minLng: number
    maxLng: number
}

export async function GetExplorePosts(authentificatedFetch: AuthenticatedFetch, bounds: ExploreBounds): Promise<Post[]> {
    const query = new URLSearchParams(
        {
            min_lat: String(bounds.minLat),
            max_lat: String(bounds.maxLat),
            min_lng: String(bounds.minLng),
            max_lng: String(bounds.maxLng),
            limit: '100'
        }
    )

    const response = await authentificatedFetch(
        `${API_BASE_URL}/explore/posts?${query.toString()}`
    )

    if (!response.ok){
        throw new Error(
            'Could not load Explore posts'
        ) 
    }

    return response.json()
}

export async function getHiddenPosts(authentificatedFetch: AuthenticatedFetch, limit = 100): Promise<Post[]> {
    const query = new URLSearchParams({
        limit: String(limit)
    })
    
    const response  = await authentificatedFetch(
        `${API_BASE_URL}/explore/recent?${query.toString()}`
    )

    if(!response.ok){
        const responseBody = await response.text();

        throw new Error(
            `Could not load recent posts: ${response.status}  ${responseBody}`
        )
    }

    return response.json()
}