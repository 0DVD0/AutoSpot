import { User, UserProfile } from "@/types/user";
import { API_BASE_URL } from "./api";
import type { AuthenticatedFetch } from "@/hooks/useAuthenticatedApi";
import { FollowStatus } from "@/types/followStatus";
import { Post } from "@/types/post";
import type { ImagePickerAsset } from "expo-image-picker";

export type UpdateUserProfileRequest = {
  username?: string;
  bio?: string | null;
};

export async function getUser(userId: number): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`) 

    if (!response.ok){
        throw new Error('User not found')
    }

    return response.json()
}

export async function getFollowStatus(user_id: number, authenticatedFetch: AuthenticatedFetch): Promise<FollowStatus> {
   const response = await authenticatedFetch(`${API_BASE_URL}/users/${user_id}/follow-status`,{
   }
   ) 

    if (!response.ok){
        throw new Error('User not found')
    }

    return response.json() 
}

export async function followUser(user_id: number, authenticatedFetch: AuthenticatedFetch): Promise<FollowStatus> {
    const response = await authenticatedFetch(`${API_BASE_URL}/users/${user_id}/follow`, {
        method: 'POST',
    }
    ) 

    if (!response.ok){
        throw new Error("Cant't follow user")
    }

    return response.json()
}
export async function unfollowUser(user_id: number, authenticatedFetch: AuthenticatedFetch): Promise<FollowStatus> {
    const response = await authenticatedFetch(`${API_BASE_URL}/users/${user_id}/follow`,{
        method: 'DELETE'
    }
    ) 

    if (!response.ok){
        throw new Error('User not found')
    }

    return response.json()
}

export async function getUserProfile(userId:number, authenticatedFetch: AuthenticatedFetch): Promise<UserProfile> {
    const response = await authenticatedFetch(`${API_BASE_URL}/users/${userId}/profile`);

    if (!response.ok){
        throw new Error('Could not load user profile')
    }

    return response.json();
}

export async function getUserPosts(user_id: number, authenticatedFetch: AuthenticatedFetch): Promise<Post[]>{
    const response = await authenticatedFetch(`${API_BASE_URL}/users/${user_id}/posts`);

    if(!response.ok){
        throw new Error('Could not load user posts')
    }

    return response.json();
}

export async function updateMyProfile(authenticatedFetch: AuthenticatedFetch, data: UpdateUserProfileRequest): Promise<User> {
    const response = await authenticatedFetch(`${API_BASE_URL}/users/me/profile`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Could not update profile');
  }

  return response.json();
}

export async function uploadAvatar(authentificateFetch: AuthenticatedFetch, image: ImagePickerAsset): Promise<User> {
    const formData = new FormData();

    const mimeType = image.mimeType ?? 'image/jpeg'

    const fileName = image.fileName ?? `avater-${Date.now()}.jpg`;

    formData.append(
        'file',
        {
            uri: image.uri,
            name: fileName,
            type: mimeType
        } as any
    )

    const response = await authentificateFetch(`${API_BASE_URL}/users/me/avatar`,
    {
        method: 'PUT',
        body: formData
    }
)

if (!response.ok){
    throw new Error('Could not upload avatar');
}

return response.json()
}

export async function deleteAvatar(authentification: AuthenticatedFetch): Promise<User> {
    const response = await authentification(
        `${API_BASE_URL}/users/me/avatar`,
        {
            method: 'DELETE'
        }
    )

    if (!response.ok){
        throw new Error('Could not delete avatar')
    }
    return response.json()
}