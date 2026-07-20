import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'autospot_access_token';
const REFRESH_KEY = 'autospot_refresh_token';

export async function saveTokens(token: string, refresh_token: string) {
    await SecureStore.setItemAsync(TOKEN_KEY, token);
    await SecureStore.setItemAsync(REFRESH_KEY, refresh_token);
}

export async function getAccessToken() {
    return SecureStore.getItemAsync(TOKEN_KEY);
}

export async function getRefreshToken() {
    return SecureStore.getItemAsync(REFRESH_KEY)
}

export async function deleteTokens() {
    await SecureStore.deleteItemAsync(TOKEN_KEY)
    await SecureStore.deleteItemAsync(REFRESH_KEY)
}