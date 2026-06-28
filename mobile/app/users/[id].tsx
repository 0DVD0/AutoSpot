import { useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { AutoSpotColors } from '@/constants/autospotTheme';
import { useAuth } from '@/context/AuthContext';
import { ProfileView } from '@/components/userView/ProfileView';
import { getUser } from '@/services/userAPI';
import { User } from '@/types/user';

export default function UserProfileScreen() {
  const { id } = useLocalSearchParams();
  const { user: currentUser } = useAuth();

  const [profileUser, setProfileUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadUser() {
      try {
        setIsLoading(true);
        setErrorMessage(null);

        const userId = Number(id);
        const data = await getUser(userId);

        setProfileUser(data);
      } catch {
        setErrorMessage('Could not load user profile');
      } finally {
        setIsLoading(false);
      }
    }

    loadUser();
  }, [id]);

  if (isLoading) {
    return (
      <View style={styles.screen}>
        <Text style={styles.stateText}>Loading profile...</Text>
      </View>
    );
  }

  if (errorMessage || !profileUser) {
    return (
      <View style={styles.screen}>
        <Text style={styles.errorText}>{errorMessage ?? 'User not found'}</Text>
      </View>
    );
  }

  const isCurrentUser = currentUser?.id === profileUser.id;

  return (
    <ProfileView
      user={profileUser}
      isCurrentUser={isCurrentUser}
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