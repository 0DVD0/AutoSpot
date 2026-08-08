import Ionicons from '@expo/vector-icons/Ionicons';
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import {ActivityIndicator, findNodeHandle, FlatList, Pressable, RefreshControl, StyleSheet, Text, View} from 'react-native';
import { CommentModal } from '@/components/posts/CommentsModal';
import { PostCard } from '@/components/posts/PostCard';
import { AutoSpotColors } from '@/constants/autospotTheme';
import { useAuth } from '@/context/AuthContext';
import { useAuthenticatedApi } from '@/hooks/useAuthenticatedApi';
import { likePost } from '@/services/api';
import { getHiddenPosts } from '@/services/explorerAPI';
import type { Post } from '@/types/post';

export default function RecentFeed() {
    const [posts, setPosts] = useState<Post[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [isRefreshing, setIsRefreshing] = useState(false)
    const [errorMessage, setErrorMessage] = useState<string | null>(null)
    const [commentPostId, setCommentPostId] = useState<number | null>(null)
    const {user, token, isLoading: isAuthLoading} = useAuth()
    const {authenticatedFetch} = useAuthenticatedApi()
    
    const loadPosts = useCallback(
        async (showFullLoading: boolean) => {
            if (isAuthLoading) {
                return
            }

            if (!token) {
                setIsLoading(false)
                router.replace('/auth/login')
                return
            }

            try {
                if (showFullLoading) {
                    setIsLoading(true)
                }

                setErrorMessage(null)

                const data = await getHiddenPosts(authenticatedFetch)

                setPosts(data)
            } catch (error) {
                console.error(
                    '[recent] Could not load posts', error
                )
            } finally {
                if (showFullLoading) {
                    setIsLoading(false)
                }
            }
        }, [authenticatedFetch, isAuthLoading, token]
    )

    useFocusEffect(
        useCallback(() => {
            void loadPosts(true)
        }, [loadPosts])
    )

    const handleRefresh = useCallback(
        async () => {
            try {
                setIsRefreshing(true)
                await loadPosts(false)
            } finally {
                setIsRefreshing(false)
            }
        }, [loadPosts]
    )

    async function handleToggleLike(
    postId: number
  ) {
    if (!token) {
      router.replace('/auth/login');
      return;
    }

    try {
      setErrorMessage(null);

      const likeStatus = await likePost(
        postId,
        authenticatedFetch
      );

      setPosts((currentPosts) =>
        currentPosts.map((post) =>
          post.id === likeStatus.post_id
            ? {
                ...post,
                likes_count:
                  likeStatus.likes_count,
                is_liked_by_me:
                  likeStatus.is_liked_by_me,
              }
            : post
        )
      );
    } catch (error) {
      console.error(
        '[recent] Could not update like',
        error
      );

      setErrorMessage(
        'Could not update the like'
      );
    }
  }

  function handleCommentCreated(
    postId: number
  ) {
    setPosts((currentPosts) =>
      currentPosts.map((post) =>
        post.id === postId
          ? {
              ...post,
              comments_count:
                post.comments_count + 1,
            }
          : post
      )
    );
  }

  function handleCommentDeleted(
    postId: number
  ) {
    setPosts((currentPosts) =>
      currentPosts.map((post) =>
        post.id === postId
          ? {
              ...post,
              comments_count: Math.max(
                post.comments_count - 1,
                0
              ),
            }
          : post
      )
    );
  }

  if (isLoading) {
    return (
      <View style={styles.centeredScreen}>
        <ActivityIndicator
          size="large"
          color={AutoSpotColors.primary}
        />

        <Text style={styles.stateText}>
          Loading recent spots...
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.screen}>
      <FlatList
        data={posts}
        keyExtractor={(post) =>
          String(post.id)
        }
        contentContainerStyle={[
          styles.list,
          posts.length === 0 &&
            styles.emptyList,
        ]}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={handleRefresh}
            tintColor={AutoSpotColors.primary}
          />
        }
        ListHeaderComponent={
          <View style={styles.listHeader}>
            <View style={styles.headerIcon}>
              <Ionicons
                name="eye-off-outline"
                size={24}
                color={AutoSpotColors.primary}
              />
            </View>

            <View style={styles.headerText}>
              <Text style={styles.title}>
                Hidden location spots
              </Text>

              <Text style={styles.subtitle}>
                These posts were shared without
                a map location.
              </Text>
            </View>
          </View>
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons
              name="images-outline"
              size={54}
              color={AutoSpotColors.subtle}
            />

            <Text style={styles.emptyTitle}>
              No hidden location spots
            </Text>

            <Text style={styles.emptyDescription}>
              New active posts without a map
              location will appear here.
            </Text>

            <Pressable
              style={styles.retryButton}
              onPress={() => {
                void loadPosts(true);
              }}
            >
              <Text style={styles.retryButtonText}>
                Try again
              </Text>
            </Pressable>
          </View>
        }
        renderItem={({ item }) => (
          <PostCard
            post={item}
            currentUserId={user?.id}
            onToggleLike={
              handleToggleLike
            }
            onOpenComments={(postId) => {
              setCommentPostId(postId);
            }}
          />
        )}
      />

      {errorMessage ? (
        <View style={styles.errorBanner}>
          <Ionicons
            name="alert-circle-outline"
            size={18}
            color={AutoSpotColors.danger}
          />

          <Text style={styles.errorText}>
            {errorMessage}
          </Text>

          <Pressable
            onPress={() => {
              void loadPosts(true);
            }}
          >
            <Text style={styles.retryText}>
              Retry
            </Text>
          </Pressable>
        </View>
      ) : null}

      <CommentModal
        visible={commentPostId !== null}
        postId={commentPostId}
        token={token}
        currentUserId={user?.id}
        onClose={() => {
          setCommentPostId(null);
        }}
        onCommentCreated={
          handleCommentCreated
        }
        onCommentDeleted={
          handleCommentDeleted
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: AutoSpotColors.background,
  },

  centeredScreen: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: AutoSpotColors.background,
    paddingHorizontal: 30,
  },

  list: {
    padding: 16,
    paddingBottom: 40,
    gap: 16,
  },

  emptyList: {
    flexGrow: 1,
  },

  listHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },

  headerIcon: {
    width: 46,
    height: 46,
    borderRadius: 23,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: AutoSpotColors.charcoal,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
  },

  headerText: {
    flex: 1,
    marginLeft: 12,
  },

  title: {
    color: AutoSpotColors.text,
    fontSize: 22,
    fontWeight: '800',
  },

  subtitle: {
    color: AutoSpotColors.muted,
    marginTop: 3,
    lineHeight: 19,
  },

  stateText: {
    color: AutoSpotColors.muted,
    marginTop: 14,
    textAlign: 'center',
  },

  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 24,
    paddingBottom: 80,
  },

  emptyTitle: {
    color: AutoSpotColors.text,
    fontSize: 19,
    fontWeight: '800',
    marginTop: 16,
  },

  emptyDescription: {
    color: AutoSpotColors.muted,
    textAlign: 'center',
    lineHeight: 20,
    marginTop: 7,
  },

  retryButton: {
    marginTop: 20,
    borderRadius: 12,
    paddingHorizontal: 18,
    paddingVertical: 11,
    backgroundColor: AutoSpotColors.primary,
  },

  retryButtonText: {
    color: AutoSpotColors.text,
    fontWeight: '800',
  },

  errorBanner: {
    position: 'absolute',
    left: 16,
    right: 16,
    bottom: 20,
    minHeight: 48,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 9,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: AutoSpotColors.danger,
    backgroundColor: AutoSpotColors.charcoal,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },

  errorText: {
    flex: 1,
    color: AutoSpotColors.text,
    fontSize: 13,
  },

  retryText: {
    color: AutoSpotColors.primary,
    fontWeight: '800',
  },
});