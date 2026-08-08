import {Text, View } from 'react-native';
import { router } from 'expo-router';
import { useAuth } from '@/context/AuthContext';
import { ProfileView } from '@/components/userView/ProfileView';
import { getUserPosts, getUserProfile } from '@/services/userAPI';
import {useState, useCallback } from 'react';
import { useAuthenticatedApi } from '@/hooks/useAuthenticatedApi';
import { UserProfile } from '@/types/user';
import { Post } from '@/types/post';
import { useFocusEffect } from '@react-navigation/native';
import {deleteUserPost, likePost, } from '@/services/api';
import { CommentModal } from '@/components/posts/CommentsModal';
export default function AccountScreen() {

  const { user, token, logout } = useAuth();
  const { authenticatedFetch } = useAuthenticatedApi();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [posts, setPosts] = useState<Post[]>([])
  const [refreshing, setRefreshing] = useState(false)
  const [commentPostId, setCommentPostId] = useState<number | null>(null);
  const loadProfile = useCallback(
    async (showFullLoading: boolean) => {
    
    if (!user) {
      return;
    }

    try {
      if (showFullLoading) {
        setIsLoading(true);
      }

      setErrorMessage(null);

      const [profileData, postsData] =
        await Promise.all([
          getUserProfile(
            user.id,
            authenticatedFetch
          ),
          getUserPosts(
            user.id,
            authenticatedFetch
          ),
        ]);

      setProfile(profileData);
      setPosts(postsData);
    } catch (error) {
      console.error(
        'Could not load account:',
        error
      );

      setErrorMessage(
        'Could not load account profile'
      );
    } finally {
      if (showFullLoading) {
        setIsLoading(false);
      }
    }
  },
  [user, authenticatedFetch]
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







  useFocusEffect(
    useCallback(() => {
      loadProfile(true);
    }, [loadProfile])
  );

  const onRefresh = async () => {
      if (!user){
        return
      }
      if(!token){
          router.replace('/auth/login')
          return
        }
  
    try {
      setRefreshing(true);
      await loadProfile(false)
    } finally {
      setRefreshing(false);
    }
  };
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

    <>
    
        <ProfileView
      profile={profile}
      posts={posts}
      currentUserId={user?.id}
      isCurrentUser
      refreshing={refreshing}
      onRefresh={onRefresh}
      onEditProfile={() =>
        router.push('/edit-profile')
      }
      onOpenSettings={() =>
        router.push('/settings')
      }
      onLogout={handleLogout}
      onDeletePost={handleDeletePost}
      onToggleLike={onToggleLike}
      onOpenComments={setCommentPostId}
      />
      <CommentModal
        visible={commentPostId !== null}
        postId={commentPostId}
        token={token}
        currentUserId={user?.id}
        onClose={() => setCommentPostId(null)}
        onCommentCreated={handleCommentCreated}
        onCommentDeleted={handleDeleteComment}
      />
    </>
  );
}
