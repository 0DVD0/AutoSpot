import { createContext, PropsWithChildren, useContext, useEffect, useState } from 'react';

import { AuthUser, getMeRequest, loginRequest, LoginRequest } from '@/services/authAPI';
import { deleteToken, getToken, saveToken } from '@/services/tokenStorage';

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadSession() {
      try {
        const storedToken = await getToken();

        if (!storedToken) {
          return;
        }

        const currentUser = await getMeRequest(storedToken);

        setToken(storedToken);
        setUser(currentUser);
      } catch {
        await deleteToken();
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    loadSession();
  }, []);

  async function login(data: LoginRequest) {
    const tokenResponse = await loginRequest(data);

    await saveToken(tokenResponse.access_token);

    const currentUser = await getMeRequest(tokenResponse.access_token);

    setToken(tokenResponse.access_token);
    setUser(currentUser);
  }

  async function logout() {
    await deleteToken();

    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
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