import { User } from "@/types/user";
import { API_BASE_URL } from "./api";

export async function getUser(userId: number): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`) 

    if (!response.ok){
        throw new Error('User not found')
    }

    return response.json()
}
