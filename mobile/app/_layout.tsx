import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import 'react-native-reanimated';
import { AuthProvider } from '@/context/AuthContext';

import { useColorScheme } from '@/hooks/use-color-scheme';

export const unstable_settings = {
  anchor: '(tabs)',
};

export default function RootLayout() {
  const colorScheme = useColorScheme();

  return (
    <AuthProvider>
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="auth" options={{headerShown: false}} />
        <Stack.Screen name="modal" options={{ presentation: 'modal', title: 'Modal' }} />
        <Stack.Screen name="settings" options={{title:'Settings', headerShown: true}} />
        <Stack.Screen name="edit-profile" options={{title:'Edit profile', headerShown: true}} />
        <Stack.Screen name="postForm" options={{title:'Post Form', headerShown: true}}/>
        <Stack.Screen name="users/[id]" options={{title: '', headerBackTitle: 'Back'}}/>
        <Stack.Screen name="recent" options={{title:'Recent', headerShown: true, headerBackTitle:'Back'}}/>
      </Stack>
      <StatusBar style="auto" />
    </ThemeProvider>
    </AuthProvider>
  );
}
