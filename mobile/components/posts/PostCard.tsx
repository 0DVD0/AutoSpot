import { Image, Modal, Pressable, StyleSheet, Text, View, Alert } from 'react-native';
import Ionicons from '@expo/vector-icons/Ionicons';
import { useState } from 'react';
import { AutoSpotColors } from '@/constants/autospotTheme';
import { Post } from '@/types/post';
import { downloadImageToLibrary } from '@/services/imageDownload';
import { router } from 'expo-router';

type PostCardProps = {
  post: Post;
  currentUserId?: number;
  onDelete?: (postId: number) => void;
  onToggleLike?: (postId: number) => void;
  onOpenComments?: (postId: number) => void;
};



function getTimeRemaining(expiresAtValue: string){
  const expiresAt = new Date(expiresAtValue);
  const now = new Date();
  const difference = expiresAt.getTime() - now.getTime();

  if (difference <= 0) {
    return 'Expired';
  }

  const totalMinutes = Math.floor(difference / 1000 / 60);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  if (hours > 0){
    return  `${hours}h left`;
  }

  return  `${minutes}m left`;
}
export function PostCard({ post, currentUserId, onDelete, onToggleLike, onOpenComments }: PostCardProps) {
  const [isMenuAvailable, setMenuVisible] = useState(false);
  const isOwner = currentUserId === post.user_id;
  const timeRemaining = getTimeRemaining(post.expires_at);
  const [imgVisible, setImgVisible] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false)

  async function handleDownloadImage(){
    if (isDownloading) return;

  try {
    setIsDownloading(true);
    await downloadImageToLibrary(post.image_url);

    
    Alert.alert('Image downloaded', 'The image has been saved to your gallery.');
  } catch (error){
    const message =
    error instanceof Error
      ? error.message
      : 'Could not download image';

  console.error('Error downloading image:', error);
  Alert.alert('Download failed', message);
  } finally {
    setIsDownloading(false);
    setMenuVisible(false);
  }
}
  return (
    <View style={styles.card}>
  <View style={styles.imageWrap}>
    <Pressable onPress={() => setImgVisible(true)}>
      <Image source={{ uri: post.image_url }} style={styles.image} />
    </Pressable>
    <Pressable style={styles.imageMenuButton} onPress={() => setMenuVisible(true)}>
      <Ionicons name="ellipsis-horizontal" size={22} color={AutoSpotColors.text} />
    </Pressable>

    <View style={styles.timeBadge}>
      <Ionicons name="time-outline" size={13} color={AutoSpotColors.amber} />
      <Text style={styles.timeBadgeText}>{timeRemaining}</Text>
    </View>
  </View>

  <View style={styles.cardBody}>
    <View style={styles.brandBlock}>
      <Text style={styles.brand}>{post.brand ?? 'Unknown brand'}</Text>
      <Text style={styles.model}>{post.model ?? 'Unknown model'}</Text>
    </View>

    <View style={styles.metaRow}>
     <Pressable
        onPress={() =>
          router.push({
            pathname: '/users/[id]',
            params: {
              id: String(post.user_id),
            },
          })
        }>
        <Text style={styles.username}>@{post.user.username}</Text>
      </Pressable>

    </View>

    <View style={styles.actionsRow}>
      <Pressable
        style={styles.actionButton}
        onPress={() => onToggleLike?.(post.id)}
      >
        <Ionicons
          name={post.is_liked_by_me ? 'heart' : 'heart-outline'}
          size={21}
          color={post.is_liked_by_me ? AutoSpotColors.danger : AutoSpotColors.muted}
        />
        <Text style={styles.actionText}>{post.likes_count}</Text>
      </Pressable>

      <Pressable style={styles.actionButton} onPress={() => onOpenComments?.(post.id)}>
        <Ionicons name="chatbubble-outline" size={20} color={AutoSpotColors.muted} />
        <Text style={styles.actionText}>{post.comments_count}</Text>
      </Pressable>
    </View>
  </View>
       <Modal
        transparent
        visible={isMenuAvailable}
        animationType="fade"
        onRequestClose={() => setMenuVisible(false)}
      >
        <Pressable style={styles.modalOverlay} onPress={() => setMenuVisible(false)}>
          <View style={styles.menu}>
            <Pressable
              style={styles.menuItem}
              onPress={handleDownloadImage}
              disabled={isDownloading}
>
            <Text style={styles.menuText}>
              {isDownloading ? 'Downloading...' : 'Download image'}
            </Text>
        </Pressable>

            {isOwner && (
              <Pressable
                style={styles.menuItem}
                onPress={() => {
                  setMenuVisible(false);
                  onDelete?.(post.id);
                }}
              >
                <Text style={styles.deleteText}>Delete post</Text>
              </Pressable>
            )}

            <Pressable style={styles.menuItem} onPress={() => setMenuVisible(false)}>
              <Text style={styles.menuText}>Cancel</Text>
            </Pressable>
          </View>
        </Pressable>
      </Modal>

      <Modal visible={imgVisible} transparent={false} animationType='fade'>
            <Pressable style={styles.imageModalOverlay} onPress={() => setImgVisible(false)}>
              <Image source={{ uri: post.image_url }} style={styles.fullImage} />
            </Pressable>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: AutoSpotColors.charcoal,
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
  },
  imageWrap: {
    position: 'relative',
    width: '100%',
    aspectRatio: 4 / 3,
    backgroundColor: AutoSpotColors.card,
  },
  image: {
    width: '100%',
    height: '100%',
  },
  imageMenuButton: {
    position: 'absolute',
    top: 12,
    right: 12,
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: 'rgba(10, 10, 15, 0.72)',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.12)',
  },
  timeBadge: {
    position: 'absolute',
    top: 12,
    left: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    paddingHorizontal: 10,
    height: 30,
    borderRadius: 15,
    backgroundColor: 'rgba(10, 10, 15, 0.72)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.12)',
  },
  timeBadgeText: {
    color: AutoSpotColors.amber,
    fontSize: 12,
    fontWeight: '800',
  },
  cardBody: {
    padding: 16,
  },
  brandBlock: {
    marginBottom: 12,
  },
  brand: {
    color: AutoSpotColors.text,
    fontSize: 22,
    fontWeight: '900',
  },
  model: {
    color: AutoSpotColors.muted,
    fontSize: 14,
    fontWeight: '600',
    marginTop: 2,
  },
  metaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: 12,
    marginBottom: 14,
  },
  username: {
    color: AutoSpotColors.muted,
    fontSize: 14,
    fontWeight: '600',
  },
  actionsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 22,
    borderTopWidth: 1,
    borderTopColor: AutoSpotColors.border,
    paddingTop: 14,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 7,
  },
  actionText: {
    color: AutoSpotColors.muted,
    fontSize: 14,
    fontWeight: '700',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.45)',
    justifyContent: 'center',
    padding: 24,
  },
  menu: {
    backgroundColor: AutoSpotColors.charcoal,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    overflow: 'hidden',
  },
  menuItem: {
    paddingVertical: 16,
    paddingHorizontal: 18,
    borderBottomWidth: 1,
    borderBottomColor: AutoSpotColors.border,
  },
  menuText: {
    color: AutoSpotColors.text,
    fontSize: 16,
    fontWeight: '700',
  },
  deleteText: {
    color: AutoSpotColors.danger,
    fontSize: 16,
    fontWeight: '800',
  },
    fullImage: {
      width: '100%',
      height: '100%',
      resizeMode: 'contain',
  },
    imageModalOverlay: {
      flex: 1,
      backgroundColor: '#000',
      justifyContent: 'center',
      alignItems: 'center',
  },
});
