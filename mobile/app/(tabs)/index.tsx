import { FlatList, StyleSheet, Text, View, RefreshControl } from 'react-native';
import { useCallback, useState } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import { getPosts, deleteUserPost, likePost } from '@/services/api';
import { Post } from '@/types/post';
import { AutoSpotColors } from '@/constants/autospotTheme';
import { PostCard } from '@/components/posts/PostCard';
import { useAuth } from '@/context/AuthContext';
import { router } from 'expo-router';
import { CommentModal } from '@/components/posts/CommentsModal';
import { useAuthenticatedApi } from '@/hooks/useAuthenticatedApi';

export default function HomeScreen() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [isPostLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const { user, token, isLoading: isAuthLoading } = useAuth();
  const { authenticatedFetch } = useAuthenticatedApi();
  const [commentPostId, setCommentsPostId] = useState<number | null>(null)
  useFocusEffect(
  useCallback(() => {
    async function loadPosts() {
      if(isAuthLoading){
        return;
      }

      if(!token){
        setIsLoading(false)
        router.replace('/auth/login')
        return
      }
      try {
        setIsLoading(true);
        setErrorMessage(null);

        const data = await getPosts(authenticatedFetch);
        setPosts(data);
      } catch {
        setErrorMessage('Could not load posts from backend');
      } finally {
        setIsLoading(false);
      }
    }

    loadPosts();
  }, [token, isAuthLoading, authenticatedFetch])
);

  const onToggleLike = async (postId: number) => {
    if(!token){
        setIsLoading(false)
        router.replace('/auth/login')
        return
      }

    try {
    setErrorMessage(null)
    const LikeStatus = await likePost(postId, authenticatedFetch);
    
    setPosts((currentPosts) => currentPosts.map((post) => post.id === LikeStatus.post_id ? {
      ...post,
      likes_count: LikeStatus.likes_count,
      is_liked_by_me: LikeStatus.is_liked_by_me,
    }: post
  )
);
  } catch {
    setErrorMessage('Could not update likes');
  }
  }

  const onRefresh = async () => {
    if(!token){
        setIsLoading(false)
        router.replace('/auth/login')
        return
      }

  try {
    setRefreshing(true);
    setErrorMessage(null);

    const data = await getPosts(authenticatedFetch);
    setPosts(data);
  } catch {
    setErrorMessage('Could not refresh posts');
  } finally {
    setRefreshing(false);
  }
};
  function handleOpenComments(postId: number){
    setCommentsPostId(postId)
  }

  function handleCommentCreated(postId: number){
    setPosts((currentPosts) =>
    currentPosts.map((post) => post.id === postId ? {
      ...post,
      comments_count: post.comments_count + 1 } : post))
  }

  function handleDeleteComment(postId: number){
    setPosts((currentPosts) => currentPosts.map((post) => post.id === postId ? {
      ...post,
      comments_count: Math.max(post.comments_count - 1,  0),
    }
  : post
))
  }
  async function handleDeletePost(postId: number) {
    if(!token) {
      setErrorMessage('You must be logged in to manage posts');
      return;
    }
  
    try {
      setErrorMessage(null);
      await deleteUserPost(postId, authenticatedFetch);

      setPosts((currentPosts) => currentPosts.filter((post) => post.id !== postId));
    } catch {
      setErrorMessage('Could not delete post');
    }
  }
  return (
    <View style={styles.screen}>
      <Text style={styles.logo}>AutoSpot</Text>
      <Text style={styles.subtitle}>Recent spots from the community</Text>

      {isPostLoading && <Text style={styles.stateText}>Loading posts...</Text>}

      {errorMessage && <Text style={styles.errorText}>{errorMessage}</Text>}
      
      {!isPostLoading && !errorMessage && (
        <FlatList
          data={posts}
          keyExtractor={(item) => String(item.id)}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            <Text style={styles.stateText}>No active posts yet.</Text>
          }
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh}/>
          }
        renderItem={({ item }) => (
          <PostCard
            post={item}
            currentUserId={user?.id}
            onDelete={handleDeletePost}
            onToggleLike={onToggleLike}
            onOpenComments={handleOpenComments}
          />
        )}
        />
      )}
      <CommentModal
        visible={commentPostId !== null}
        postId={commentPostId}
        token={token}
        currentUserId={user?.id}
        onClose={() => setCommentsPostId(null)}
        onCommentCreated={handleCommentCreated}
        onCommentDeleted={handleDeleteComment}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: AutoSpotColors.background,
    paddingHorizontal: 16,
    paddingTop: 56,
  },
  logo: {
    color: AutoSpotColors.text,
    fontSize: 26,
    fontWeight: '800',
  },
  subtitle: {
    color: AutoSpotColors.muted,
    marginTop: 4,
    marginBottom: 20,
  },
  list: {
    paddingBottom: 120,
    gap: 16,
  },
  stateText: {
    color: AutoSpotColors.muted,
    marginTop: 20,
  },
  errorText: {
    color: AutoSpotColors.danger,
    marginTop: 20,
    fontWeight: '700',
  },
});
