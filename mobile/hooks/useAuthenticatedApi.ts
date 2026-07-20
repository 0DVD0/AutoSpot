import { useCallback } from 'react';
import { router } from 'expo-router';

import { useAuth } from '@/context/AuthContext';

export type AuthenticatedFetch = (
  input: string,
  init?: RequestInit
) => Promise<Response>;

export function useAuthenticatedApi() {
  const { token, refreshSession, logout } = useAuth();

  const authenticatedFetch = useCallback<AuthenticatedFetch>(
    async (input, init = {}) => {
      if (!token) {
        router.replace('/auth/login');
        throw new Error('UNAUTHENTICATED');
      }

      function buildRequestInit(accessToken: string): RequestInit {
        const headers = new Headers(init.headers);
        headers.set('Authorization', `Bearer ${accessToken}`);

        return {
          ...init,
          headers,
        };
      }

      let response = await fetch(input, buildRequestInit(token));

      if (response.status !== 401) {
        return response;
      }

      const refreshedAccessToken = await refreshSession();

      if (!refreshedAccessToken) {
        router.replace('/auth/login');
        throw new Error('UNAUTHENTICATED');
      }

      response = await fetch(input, buildRequestInit(refreshedAccessToken));

      if (response.status === 401) {
        await logout();
        router.replace('/auth/login');
        throw new Error('UNAUTHENTICATED');
      }

      return response;
    },
    [token, refreshSession, logout]
  );

  return {
    authenticatedFetch,
  };
}
