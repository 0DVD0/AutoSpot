import Ionicons from '@expo/vector-icons/Ionicons';
import { router } from 'expo-router';
import { useEffect, useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { AutoSpotColors } from '@/constants/autospotTheme';
import { useAuth } from '@/context/AuthContext';
import { useAuthenticatedApi } from '@/hooks/useAuthenticatedApi';
import { updateMyProfile } from '@/services/userAPI';

export default function EditProfileScreen() {
  const { user, refreshSession } = useAuth();
  const { authenticatedFetch } = useAuthenticatedApi();

  const [username, setUsername] = useState('');
  const [bio, setBio] = useState('');
  const [avatarUrl, setAvatarUrl] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      return;
    }

    setUsername(user.username);
    setBio(user.bio ?? '');
    setAvatarUrl(user.avatar_url ?? '');
  }, [user]);

  async function handleSave() {
    const trimmedUsername = username.trim();
    const trimmedBio = bio.trim();
    const trimmedAvatarUrl = avatarUrl.trim();

    if (!trimmedUsername) {
      setErrorMessage('Username is required.');
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);

      await updateMyProfile(authenticatedFetch, {
        username: trimmedUsername,
        bio: trimmedBio || null,
        avatar_url: trimmedAvatarUrl || null,
      });

      await refreshSession();

      router.back();
    } catch {
      setErrorMessage('Could not update profile.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.screen}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.form}>
        <Text style={styles.title}>Edit profile</Text>

        <View style={styles.field}>
          <Text style={styles.label}>Username</Text>
          <View style={styles.inputWrap}>
            <Ionicons name="person-outline" size={18} color={AutoSpotColors.subtle} />
            <TextInput
              value={username}
              onChangeText={setUsername}
              placeholder="username"
              placeholderTextColor={AutoSpotColors.subtle}
              autoCapitalize="none"
              style={styles.input}
            />
          </View>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Avatar URL</Text>
          <View style={styles.inputWrap}>
            <Ionicons name="image-outline" size={18} color={AutoSpotColors.subtle} />
            <TextInput
              value={avatarUrl}
              onChangeText={setAvatarUrl}
              placeholder="https://example.com/avatar.jpg"
              placeholderTextColor={AutoSpotColors.subtle}
              autoCapitalize="none"
              keyboardType="url"
              style={styles.input}
            />
          </View>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Bio</Text>
          <TextInput
            value={bio}
            onChangeText={setBio}
            placeholder="Tell people what you spot..."
            placeholderTextColor={AutoSpotColors.subtle}
            multiline
            maxLength={100}
            style={styles.bioInput}
          />
          <Text style={styles.counter}>{bio.length}/100</Text>
        </View>

        {errorMessage && <Text style={styles.error}>{errorMessage}</Text>}

        <Pressable
          style={[styles.saveButton, isSubmitting && styles.disabledButton]}
          onPress={handleSave}
          disabled={isSubmitting}
        >
          <Text style={styles.saveButtonText}>
            {isSubmitting ? 'Saving...' : 'Save changes'}
          </Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: AutoSpotColors.background,
  },
  form: {
    flex: 1,
    padding: 20,
    paddingTop: 28,
  },
  title: {
    color: AutoSpotColors.text,
    fontSize: 24,
    fontWeight: '800',
    marginBottom: 24,
  },
  field: {
    marginBottom: 16,
  },
  label: {
    color: AutoSpotColors.text,
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
    marginBottom: 8,
  },
  inputWrap: {
    height: 52,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    borderRadius: 10,
    backgroundColor: AutoSpotColors.charcoal,
    paddingHorizontal: 14,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  input: {
    flex: 1,
    color: AutoSpotColors.text,
    fontSize: 15,
  },
  bioInput: {
    minHeight: 110,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    borderRadius: 10,
    backgroundColor: AutoSpotColors.charcoal,
    padding: 14,
    color: AutoSpotColors.text,
    fontSize: 15,
    textAlignVertical: 'top',
  },
  counter: {
    color: AutoSpotColors.subtle,
    marginTop: 6,
    textAlign: 'right',
    fontSize: 12,
  },
  error: {
    color: AutoSpotColors.danger,
    marginBottom: 12,
    fontWeight: '700',
  },
  saveButton: {
    height: 52,
    borderRadius: 10,
    backgroundColor: AutoSpotColors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 4,
  },
  saveButtonText: {
    color: AutoSpotColors.text,
    fontWeight: '900',
    textTransform: 'uppercase',
  },
  disabledButton: {
    opacity: 0.65,
  },
});
