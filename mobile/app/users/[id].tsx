import { useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { AutoSpotColors } from '@/constants/autospotTheme';
import { useAuth } from '@/context/AuthContext';
import { ProfileView } from '@/components/userView/ProfileView';
import { followUser, getUserPosts, getUserProfile, unfollowUser } from '@/services/userAPI';
import { UserProfile } from '@/types/user';
import { useAuthenticatedApi } from '@/hooks/useAuthenticatedApi';
import { Post } from '@/types/post';

export default function UserProfileScreen() {
  const { id } = useLocalSearchParams();
  const { user: currentUser } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isFollowLoading, setIsFollowLoading] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const { authenticatedFetch } = useAuthenticatedApi();
  const [posts, setPosts] = useState<Post[]>([])

  useEffect(() => {
  async function loadUser() {
    try {
      setIsLoading(true);
      setErrorMessage(null);

      const userId = Number(id);
      const data = await getUserProfile(userId, authenticatedFetch);
      const posts = await getUserPosts(userId, authenticatedFetch)
      setProfile(data);
      setPosts(posts);
    } catch {
      setErrorMessage('Could not load user profile');
    } finally {
      setIsLoading(false);
    }
  }

  loadUser();
}, [id, authenticatedFetch]);

async function handleToggleFollow() {
  if (!profile) {
    return;
  }

  try {
    setIsFollowLoading(true);
    setErrorMessage(null);

    const newStatus = profile.is_followed_by_me
      ? await unfollowUser(profile.id, authenticatedFetch)
      : await followUser(profile.id, authenticatedFetch);

    setProfile((currentProfile) => {
      if (!currentProfile) return currentProfile;

      return {
        ...currentProfile,
        followers_count: newStatus.followers_count,
        following_count: newStatus.following_count,
        is_followed_by_me: newStatus.is_followed_by_me,
      };
    }); 
  } catch {
    setErrorMessage('Could not update follow status');
  } finally {
    setIsFollowLoading(false);
  }
}
  if (isLoading) {
    return (
      <View style={styles.screen}>
        <Text style={styles.stateText}>Loading profile...</Text>
      </View>
    );
  }

  if (errorMessage || !profile) {
    return (
      <View style={styles.screen}>
        <Text style={styles.errorText}>{errorMessage ?? 'User not found'}</Text>
      </View>
    );
  }

  const isCurrentUser = currentUser?.id === profile.id;

  return (
    <ProfileView
      profile={profile}
      posts={posts}
      currentUserId={currentUser?.id}
      isCurrentUser={isCurrentUser}
      isFollowLoading={isFollowLoading}
      onToggleFollow={handleToggleFollow}
    />
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: AutoSpotColors.background,
    padding: 16,
    paddingTop: 72,
  },
  stateText: {
    color: AutoSpotColors.muted,
  },
  errorText: {
    color: AutoSpotColors.danger,
    fontWeight: '700',
  },
});