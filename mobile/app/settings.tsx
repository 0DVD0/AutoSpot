import { router } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { AutoSpotColors } from '@/constants/autospotTheme';
import { useAuth } from '@/context/AuthContext';

export default function SettingsScreen() {
  const { logout } = useAuth();

  async function handleLogout() {
    await logout();
    router.replace('/auth/login');
  }

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Settings</Text>

      <Pressable style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>Log out</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: AutoSpotColors.background,
    padding: 20,
    paddingTop: 40,
  },
  title: {
    color: AutoSpotColors.text,
    fontSize: 24,
    fontWeight: '800',
    marginBottom: 24,
  },
  logoutButton: {
    height: 48,
    borderRadius: 10,
    backgroundColor: AutoSpotColors.danger,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoutText: {
    color: AutoSpotColors.text,
    fontWeight: '800',
    fontSize: 15,
  },
});
