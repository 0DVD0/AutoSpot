import { createContext, PropsWithChildren, useContext, useEffect, useState } from 'react';

import { AuthUser, getMeRequest, loginRequest, LoginRequest, logoutRequest, refreshTokenRequest } from '@/services/authAPI';
import { deleteTokens, getAccessToken, getRefreshToken, saveTokens } from '@/services/tokenStorage';

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<string | null>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadSession() {
  try {
    const storedAccessToken = await getAccessToken();
    const storedRefreshToken = await getRefreshToken();

    if (!storedAccessToken || !storedRefreshToken) {
      return;
    }

    try {
      const currentUser = await getMeRequest(storedAccessToken);

      setToken(storedAccessToken);
      setUser(currentUser);
    } catch {
      const newTokens = await refreshTokenRequest(storedRefreshToken);

      await saveTokens(newTokens.access_token, newTokens.refresh_token);

      const currentUser = await getMeRequest(newTokens.access_token);

      setToken(newTokens.access_token);
      setUser(currentUser);
    }
  } catch {
    await deleteTokens();
    setToken(null);
    setUser(null);
  } finally {
    setIsLoading(false);
  }
}
    loadSession();
  }, []);

  async function refreshSession(): Promise<string | null> {
  try {
    const storedRefreshToken = await getRefreshToken();

    if (!storedRefreshToken) {
      await deleteTokens();
      setToken(null);
      setUser(null);
      return null;
    }

    const newTokens = await refreshTokenRequest(storedRefreshToken);

    await saveTokens(newTokens.access_token, newTokens.refresh_token);

    const currentUser = await getMeRequest(newTokens.access_token);

    setToken(newTokens.access_token);
    setUser(currentUser);

    return newTokens.access_token;
  } catch {
    await deleteTokens();
    setToken(null);
    setUser(null);

    return null;
  }
}
  async function login(data: LoginRequest) {
    const tokenResponse = await loginRequest(data);

    await saveTokens(tokenResponse.access_token, tokenResponse.refresh_token);

    const currentUser = await getMeRequest(tokenResponse.access_token);

    setToken(tokenResponse.access_token);
    setUser(currentUser);
  }

  async function logout() {
  try {
    const storedRefreshToken = await getRefreshToken();

    if (storedRefreshToken) {
      await logoutRequest(storedRefreshToken);
    }
  } catch {
    // Even if backend logout fails, local logout should still happen.
  } finally {
    await deleteTokens();

    setToken(null);
    setUser(null);
  }
}

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout, refreshSession }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }

  return context;
}