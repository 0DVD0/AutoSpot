import {Text, View } from 'react-native';
import { router } from 'expo-router';
import { useAuth } from '@/context/AuthContext';
import { ProfileView } from '@/components/userView/ProfileView';
export default function AccountScreen() {

  const { user, logout } = useAuth();

  async function handleLogout() {
    await logout();
    router.replace('/auth/login');
  }
  
  if(!user){
    return(
      <View>
        <Text>
          Loading account...
        </Text>
      </View>
    )
  }
  return (
    <ProfileView
      user={user}
      isCurrentUser={true}
      onLogout={handleLogout}
    />
  );
}
