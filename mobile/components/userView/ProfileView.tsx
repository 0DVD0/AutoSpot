import Ionicons from '@expo/vector-icons/Ionicons';
import { FlatList, Pressable, StyleSheet, Text, View, RefreshControl, Image } from 'react-native';

import { AutoSpotColors } from '@/constants/autospotTheme';
import { Post } from '@/types/post';
import { UserProfile } from '@/types/user';
import { PostCard } from '../posts/PostCard';

type ProfileViewProps = {
  profile: UserProfile;
  posts: Post[];
  currentUserId?: number;
  isCurrentUser: boolean;
  isFollowLoading?: boolean;
  onDeletePost?: (postId: number) => void
  onToggleLike?: (postId: number) => void
  onOpenComments?: (postId: number) => void
  refreshing?: boolean;
  onRefresh?: () => void;
  onEditProfile?: () => void;
  onOpenSettings?: () => void;
  onToggleFollow?: () => void;
  onLogout?: () => void;
};

export function ProfileView({
  profile,
  isCurrentUser,
  onEditProfile,
  refreshing,
  onRefresh,
  onOpenSettings,
  onLogout,
  onToggleFollow,
  onDeletePost,
  onOpenComments,
  onToggleLike,
  isFollowLoading,
  posts,
  currentUserId,
}: ProfileViewProps) {
  return (
    <FlatList
      data={posts}
      keyExtractor={(item) => String(item.id)}
      ItemSeparatorComponent={() => (
        <View style={styles.postSeparator} />
      )}
      refreshControl={
        onRefresh ? (
          <RefreshControl
            refreshing={refreshing ?? false}
            onRefresh={onRefresh}
          />
        ) : undefined
      }
      ListHeaderComponent={
        <View style={styles.screen}>
          {isCurrentUser && (
            <Pressable style={styles.settingsButton} onPress={onOpenSettings}>
              <Ionicons name="settings-outline" size={22} color={AutoSpotColors.text} />
            </Pressable>
          )}

        {profile.avatar_url ? (
          <Image
            source={{ uri: profile.avatar_url }}
            style={styles.avatar}
          />
        ) : (
          <View style={styles.avatar}>
            <Ionicons
              name="person"
              size={42}
              color={AutoSpotColors.subtle}
            />
          </View>
        )}
          <Text style={styles.username}>@{profile.username}</Text>
          <Text style={styles.bio}>{profile.bio ?? 'Car enthusiast profile'}</Text>

          <View style={styles.stats}>
            <View>
              <Text style={styles.statNumber}>{profile.following_count}</Text>
              <Text style={styles.statLabel}>Following</Text>
            </View>

            <View>
              <Text style={styles.statNumber}>{profile.followers_count}</Text>
              <Text style={styles.statLabel}>Followers</Text>
            </View>

            <View>
              <Text style={styles.statNumber}>{profile.groups_count}</Text>
              <Text style={styles.statLabel}>Groups</Text>
            </View>
          </View>

          {isCurrentUser ? (
            <Pressable style={styles.editProfileButton} onPress={onEditProfile}>
              <Text style={styles.editProfileText}>Edit profile</Text>
            </Pressable>
          ) : (
            <Pressable
              style={[
                styles.followButton,
                profile.is_followed_by_me && styles.followingButton,
                isFollowLoading && styles.disabledButton,
              ]}
              onPress={onToggleFollow}
              disabled={isFollowLoading}
            >
              <Text style={styles.followText}>
                {isFollowLoading
                  ? 'Loading...'
                  : profile.is_followed_by_me
                    ? 'Following'
                    : 'Follow'}
              </Text>
            </Pressable>
          )}

          <View style={styles.postsDivider} />
        </View>
      }
      renderItem={({ item }) => (
        <PostCard
          post={item}
          currentUserId={currentUserId}
          onDelete={onDeletePost}
          onOpenComments={onOpenComments}
          onToggleLike={onToggleLike}
        />
      )}
    />
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
  settingsButton: {
    position: 'absolute',
    top: 58,
    right: 16,
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: AutoSpotColors.charcoal,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
  },
  avatar: {
    width: 96,
    height: 96,
    borderRadius: 48,
    alignItems: 'center',
    justifyContent: 'center',
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
  editProfileButton: {
    marginTop: 28,
    height: 48,
    paddingHorizontal: 28,
    borderRadius: 10,
    backgroundColor: AutoSpotColors.card,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  editProfileText: {
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
  followingButton: {
    backgroundColor: AutoSpotColors.card,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
  },
  disabledButton: {
    opacity: 0.65,
  },
  postsDivider: {
    width: '100%',
    marginTop: 32,
    marginBottom: 18,
    paddingTop: 18,
    borderTopWidth: 1,
    borderTopColor: AutoSpotColors.border,
  },
  postSeparator: {
  height: 16,
  },
});
