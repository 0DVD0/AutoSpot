import { User } from "@/types/user"
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { AutoSpotColors } from '@/constants/autospotTheme';
type ProfileViewProps = {
    user: User
    isCurrentUser: boolean
    onLogout?: () => void
}
export function ProfileView({user, isCurrentUser, onLogout}: ProfileViewProps ){

    return(
        <View style={styles.screen}>
      <View style={styles.avatar} />

      <Text style={styles.username}>@{user.username}</Text>
      <Text style={styles.bio}>{user.bio ?? 'Car enthusiast profile'}</Text>

      <View style={styles.stats}>
        <View>
          <Text style={styles.statNumber}>24</Text>
          <Text style={styles.statLabel}>Spots</Text>
        </View>

        <View>
          <Text style={styles.statNumber}>128</Text>
          <Text style={styles.statLabel}>Followers</Text>
        </View>

        <View>
          <Text style={styles.statNumber}>12</Text>
          <Text style={styles.statLabel}>Groups</Text>
        </View>
      </View>

      {isCurrentUser ? (
        <Pressable style={styles.logoutButton} onPress={onLogout}>
          <Text style={styles.logoutText}>Log out</Text>
        </Pressable>
      ) : (
        <Pressable style={styles.followButton}>
          <Text style={styles.followText}>Follow</Text>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: AutoSpotColors.background,
    padding: 16,
    paddingTop: 72,
    alignItems: 'center',
  },
  avatar: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: AutoSpotColors.charcoal,
    borderWidth: 2,
    borderColor: AutoSpotColors.primary,
  },
  username: {
    color: AutoSpotColors.text,
    fontSize: 24,
    fontWeight: '800',
    marginTop: 18,
  },
  bio: {
    color: AutoSpotColors.muted,
    marginTop: 6,
  },
  stats: {
    marginTop: 28,
    flexDirection: 'row',
    gap: 28,
    backgroundColor: AutoSpotColors.charcoal,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    padding: 20,
  },
  statNumber: {
    color: AutoSpotColors.text,
    fontSize: 20,
    fontWeight: '800',
    textAlign: 'center',
  },
  statLabel: {
    color: AutoSpotColors.muted,
    marginTop: 4,
    textAlign: 'center',
  },
  logoutButton: {
    marginTop: 28,
    height: 48,
    paddingHorizontal: 28,
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
  followButton: {
    marginTop: 28,
    height: 48,
    paddingHorizontal: 28,
    borderRadius: 10,
    backgroundColor: AutoSpotColors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  followText: {
    color: AutoSpotColors.text,
    fontWeight: '800',
    fontSize: 15,
  },
})