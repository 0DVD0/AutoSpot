import { API_BASE_URL } from "./api";

export type LoginRequest = {
    email: string;
    password: string;
};

export type RegisterRequest = {
    username: string;
    email: string;
    password: string;
    avatar_url: string | null;
    bio?: string |null;
};

export type AuthUser = {
    id: number;
    username: string;
    email: string;
    avatar_url: string | null;
    bio: string | null;
    created_at: string;
};

export type TokenResponse = {
    access_token: string;
    token_type: string;
};

export async function loginRequest(data: LoginRequest): Promise<TokenResponse> {
    const response = await fetch (`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });

    if (!response.ok){
        throw new Error('Invalid email or password');
    }

    return response.json();
}

export async function registerRequest(data: RegisterRequest): Promise<AuthUser> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    
    if (!response.ok){
        throw new Error('Could not create account');
    }

    return response.json()
}

export async function getMeRequest(token: string): Promise<AuthUser> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers:{
            Authorization: `Bearer ${token}`,
        },
    });

    if (!response.ok){
        throw new Error('Could not load current user');
    }

    return response.json();
}