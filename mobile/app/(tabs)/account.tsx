import {Text, View } from 'react-native';
import { router } from 'expo-router';
import { useAuth } from '@/context/AuthContext';
import { ProfileView } from '@/components/userView/ProfileView';
import { getUserPosts, getUserProfile } from '@/services/userAPI';
import { useEffect, useState } from 'react';
import { useAuthenticatedApi } from '@/hooks/useAuthenticatedApi';
import { UserProfile } from '@/types/user';
import { Post } from '@/types/post';

export default function AccountScreen() {

  const { user, logout } = useAuth();
  const { authenticatedFetch } = useAuthenticatedApi();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [posts, setPosts] = useState<Post[]>([])
  useEffect(() => {
    async function loadProfile() {
      if (!user) {
        return;
      }

      try {
        setIsLoading(true);
        setErrorMessage(null);

        const data = await getUserProfile(user.id, authenticatedFetch);
        const posts = await getUserPosts(user.id, authenticatedFetch)
        setProfile(data);
        setPosts(posts)
      } catch {
        setErrorMessage('Could not load account profile');
      } finally {
        setIsLoading(false);
      }
    }

    loadProfile();
  }, [user?.id, authenticatedFetch, user]);

  async function handleLogout() {
    await logout();
    router.replace('/auth/login');
  }

  if (isLoading) {
    return (
      <View>
        <Text>Loading account...</Text>
      </View>
    );
  }

  if (errorMessage || !profile) {
    return (
      <View>
        <Text>{errorMessage ?? 'Account not found'}</Text>
      </View>
    );
  }

  return (
    <ProfileView
      profile={profile}
      posts={posts}
      currentUserId={user?.id}
      isCurrentUser={true}
      onEditProfile={() => router.push('/edit-profile')}
      onOpenSettings={() => router.push('/settings')}
      onLogout={handleLogout}
    />
  );
}
