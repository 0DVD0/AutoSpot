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
  Image
} from 'react-native';

import { AutoSpotColors } from '@/constants/autospotTheme';
import { useAuth } from '@/context/AuthContext';
import { useAuthenticatedApi } from '@/hooks/useAuthenticatedApi';
import { deleteAvatar, updateMyProfile, uploadAvatar } from '@/services/userAPI';
import * as ImagePicker from 'expo-image-picker';


export default function EditProfileScreen() {
  const { user, refreshSession } = useAuth();
  const { authenticatedFetch } = useAuthenticatedApi();

  const [username, setUsername] = useState('');
  const [bio, setBio] = useState('');
  const [selectedAvatar, setSelectedAvatar] = useState<ImagePicker.ImagePickerAsset | null>(null)
  const [shouldRemoveAvatar, setShouldRemoveAvatar] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const displayedAvatarUri =
  selectedAvatar?.uri ??
  (shouldRemoveAvatar ? null : user?.avatar_url ?? null);
  useEffect(() => {
    if (!user) {
      return;
    }

    setUsername(user.username);
    setBio(user.bio ?? '');
  }, [user]);

  async function chooseAvatar() {
  try {
    setErrorMessage(null);

    const result =
      await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.7,
      });

    if (!result.canceled && result.assets.length > 0) {
      setSelectedAvatar(result.assets[0]);
      setShouldRemoveAvatar(false);
    }
  } catch (error) {
    console.error('[avatar] Gallery error:', error);
    setErrorMessage('Could not select the photo.');
  }
}

async function takeAvatarPhoto() {
  let permission =
    await ImagePicker.getCameraPermissionsAsync();

  if (!permission.granted) {
    permission =
      await ImagePicker.requestCameraPermissionsAsync();
  }

  if (!permission.granted) {
    setErrorMessage('Camera permission is required.');
    return;
  }

  const result = await ImagePicker.launchCameraAsync({
    mediaTypes: ['images'],
    allowsEditing: true,
    aspect: [1, 1],
    quality: 0.7,
  });

  if (!result.canceled && result.assets.length > 0) {
    setSelectedAvatar(result.assets[0]);
    setShouldRemoveAvatar(false);
  }
}

function markAvatarForRemoval() {
  setSelectedAvatar(null);
  setShouldRemoveAvatar(true);
}

  async function handleSave() {
    const trimmedUsername = username.trim();
    const trimmedBio = bio.trim();

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
});

if (selectedAvatar) {
  await uploadAvatar(
    authenticatedFetch,
    selectedAvatar,
  );
} else if (shouldRemoveAvatar) {
  await deleteAvatar(authenticatedFetch);
}

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
          <View style={styles.avatarSection}>
  {displayedAvatarUri ? (
    <Image
      source={{ uri: displayedAvatarUri }}
      style={styles.avatarPreview}
    />
  ) : (
    <View style={styles.avatarPlaceholder}>
      <Ionicons
        name="person"
        size={46}
        color={AutoSpotColors.subtle}
      />
    </View>
  )}

  <View style={styles.avatarActions}>
    <Pressable
      style={styles.avatarButton}
      onPress={takeAvatarPhoto}
      disabled={isSubmitting}
    >
      <Text style={styles.avatarButtonText}>
        Take photo
      </Text>
    </Pressable>

    <Pressable
      style={styles.avatarButton}
      onPress={chooseAvatar}
      disabled={isSubmitting}
    >
      <Text style={styles.avatarButtonText}>
        Choose photo
      </Text>
    </Pressable>
  </View>

  {displayedAvatarUri ? (
    <Pressable
      onPress={markAvatarForRemoval}
      disabled={isSubmitting}
    >
      <Text style={styles.removeAvatarText}>
        Remove avatar
      </Text>
    </Pressable>
  ) : null}
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
  avatarSection: {
  alignItems: 'center',
  marginBottom: 24,
},

avatarPreview: {
  width: 120,
  height: 120,
  borderRadius: 60,
  borderWidth: 2,
  borderColor: AutoSpotColors.primary,
},

avatarPlaceholder: {
  width: 120,
  height: 120,
  borderRadius: 60,
  borderWidth: 2,
  borderColor: AutoSpotColors.primary,
  backgroundColor: AutoSpotColors.charcoal,
  alignItems: 'center',
  justifyContent: 'center',
},

avatarActions: {
  flexDirection: 'row',
  gap: 12,
  marginTop: 14,
},

avatarButton: {
  minHeight: 42,
  paddingHorizontal: 16,
  borderRadius: 10,
  borderWidth: 1,
  borderColor: AutoSpotColors.border,
  backgroundColor: AutoSpotColors.charcoal,
  alignItems: 'center',
  justifyContent: 'center',
},

avatarButtonText: {
  color: AutoSpotColors.text,
  fontWeight: '700',
},

removeAvatarText: {
  color: AutoSpotColors.danger,
  marginTop: 14,
  fontWeight: '700',
},
});
