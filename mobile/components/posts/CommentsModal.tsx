import { useEffect, useState } from "react";
import {
  FlatList,
  Modal,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
  KeyboardAvoidingView,
Platform,
Keyboard,
TouchableWithoutFeedback,
} from 'react-native';
import Ionicons from '@expo/vector-icons/Ionicons';

import { AutoSpotColors } from '@/constants/autospotTheme';
import { createPostComment, getPostComments } from '@/services/api';
import { Comment } from '@/types/comment';

type CommentsProps = {
  visible: boolean
  postId: number | null
  token: string | null
  onClose: () => void
  onCommentCreated: (postId: number) => void
};

export function CommentModal({ visible, postId, token, onClose, onCommentCreated}: CommentsProps){
    const [comments, setComments] = useState<Comment[]>([])
    const [content, setContent] = useState('');
    const [isCommentsLoading, setIsCommentsLoading] = useState(true)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [errorMessage, setErrorMessage] = useState<string | null>(null) 

useEffect(() => {
    async function loadComments() {
      if (!visible || postId === null) {
        return;
      }

      try {
        setIsCommentsLoading(true);
        setErrorMessage(null);

        const data = await getPostComments(postId);
        setComments(data);
      } catch {
        setErrorMessage('Could not load comments');
      } finally {
        setIsCommentsLoading(false);
      }
    }

    loadComments();
  }, [visible, postId]);

  async function handleSubmitComment() {
    if (postId === null || !token) {
      return;
    }

    const trimmedContent = content.trim();

    if (!trimmedContent) {
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);

      const createdComment = await createPostComment(
        postId,
        token,
        trimmedContent
      );

      setComments((currentComments) => [...currentComments, createdComment]);
      setContent('');
      onCommentCreated(postId);
    } catch {
      setErrorMessage('Could not create comment');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
        <KeyboardAvoidingView
        style={styles.overlay}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={0}
        >
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>    
    
      <View style={styles.overlayInner}>
        <View style={styles.sheet}>
          <View style={styles.header}>
            <Text style={styles.title}>Comments</Text>

            <Pressable onPress={onClose} style={styles.closeButton}>
              <Ionicons name="close" size={22} color={AutoSpotColors.text} />
            </Pressable>
          </View>

          {isCommentsLoading && (
            <Text style={styles.stateText}>Loading comments...</Text>
          )}

          {errorMessage && (
            <Text style={styles.errorText}>{errorMessage}</Text>
          )}

          {!isCommentsLoading && (
            <FlatList
              data={comments}
              keyExtractor={(item) => String(item.id)}
              style={styles.list}
              contentContainerStyle={styles.listContent}
              ListEmptyComponent={
                <Text style={styles.stateText}>No comments yet.</Text>
              }
              renderItem={({ item }) => (
                <View style={styles.commentItem}>
                  <Text style={styles.username}>@{item.user.username}</Text>
                  <Text style={styles.commentText}>{item.content}</Text>
                </View>
              )}
            />
          )}

          <View style={styles.inputRow}>
            <TextInput
              value={content}
              onChangeText={setContent}
              placeholder="Write a comment..."
              placeholderTextColor={AutoSpotColors.subtle}
              style={styles.input}
              multiline
            />

            <Pressable
              style={[
                styles.sendButton,
                (!content.trim() || isSubmitting) && styles.sendButtonDisabled,
              ]}
              onPress={handleSubmitComment}
              disabled={!content.trim() || isSubmitting}
            >
              <Ionicons name="send" size={18} color={AutoSpotColors.text} />
            </Pressable>
          </View>
        </View>
      </View>
    </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.55)',
    justifyContent: 'flex-end',
  },
  sheet: {
    maxHeight: '78%',
    backgroundColor: AutoSpotColors.charcoal,
    borderTopLeftRadius: 18,
    borderTopRightRadius: 18,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    paddingHorizontal: 16,
    paddingTop: 14,
    paddingBottom: 20,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  title: {
    color: AutoSpotColors.text,
    fontSize: 18,
    fontWeight: '800',
  },
  closeButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: AutoSpotColors.card,
  },
  list: {
    maxHeight: 360,
  },
  listContent: {
    gap: 12,
    paddingBottom: 16,
  },
  commentItem: {
    backgroundColor: AutoSpotColors.card,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    padding: 12,
  },
  username: {
    color: AutoSpotColors.primary,
    fontSize: 13,
    fontWeight: '800',
    marginBottom: 4,
  },
  commentText: {
    color: AutoSpotColors.text,
    fontSize: 14,
    lineHeight: 20,
  },
  stateText: {
    color: AutoSpotColors.muted,
    paddingVertical: 16,
  },
  errorText: {
    color: AutoSpotColors.danger,
    paddingVertical: 12,
    fontWeight: '700',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 10,
    borderTopWidth: 1,
    borderTopColor: AutoSpotColors.border,
    paddingTop: 12,
  },
  input: {
    flex: 1,
    minHeight: 42,
    maxHeight: 96,
    backgroundColor: AutoSpotColors.card,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    paddingHorizontal: 12,
    paddingVertical: 10,
    color: AutoSpotColors.text,
    fontSize: 14,
  },
  sendButton: {
    width: 42,
    height: 42,
    borderRadius: 21,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: AutoSpotColors.primary,
  },
  sendButtonDisabled: {
    backgroundColor: AutoSpotColors.border,
  },
  overlayInner: {
  flex: 1,
  justifyContent: 'flex-end',
  },
});