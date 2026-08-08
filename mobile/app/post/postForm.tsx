import { router, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { useCurrentLocation } from '@/hooks/useCurrentLocation';
import {
  Image,
  KeyboardAvoidingView,
  Linking,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import type { ImagePickerAsset } from 'expo-image-picker';
import type { LocationVisibility } from '@/types/post';
import { AutoSpotColors } from '@/constants/autospotTheme';
import { useAuth } from '@/context/AuthContext';
import { useAuthenticatedApi } from '@/hooks/useAuthenticatedApi';
import { createPost } from '@/services/api';
import { uploadPostImage } from '@/services/uploadAPI';

type PostFormParams = {
  imageUri: string;
  fileName: string;
  mimeType: string;
  width: string;
  height: string;
};
const locationVisibilityOptions: {
  value: LocationVisibility
  title: string
  description: string
}[] = [
  {
    value: 'approximate',
    title: 'Approximate',
    description: 'Show an approximate area of about 100 meters'
  },
  {
    value: 'public',
    title: 'Public',
    description: 'Show the specific location of the post'
  },
  {
    value: 'private',
    title: 'Private',
    description: 'Hide the location of the post'
  }
]

export default function PostFormScreen() {
  
  const params = useLocalSearchParams<PostFormParams>();

  const { token } = useAuth();
  const { authenticatedFetch } = useAuthenticatedApi();
  const {
      coordinates, status: locationStatus, errorMessage: locationError, canAskAgain, refreshLocation
    } = useCurrentLocation();
  const [brand, setBrand] = useState('');
  const [model, setModel] = useState('');
  const [locationVisibility, setLocationVisibility] = useState<LocationVisibility>('approximate')
  const [submissionStage, setSubmissionStage] = useState<
    'idle' | 'uploading' | 'creating'
  >('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const isSubmitting = submissionStage !== 'idle';
  const requiresLocation = locationVisibility !== 'private';

  const canCreatePost =
    !isSubmitting &&
    (
      !requiresLocation ||
      (
        locationStatus === 'ready' &&
        coordinates !== null
      )
    );

  const submitButtonText =
    submissionStage === 'uploading'
      ? 'Uploading image...'
      : submissionStage === 'creating'
        ? 'Creating post...'
        : 'Create post';

  /*
   * Reconstruim obiectul de care uploadPostImage are nevoie.
   */
  const image: ImagePickerAsset = {
    uri: params.imageUri,
    fileName: params.fileName || `autospot-${Date.now()}.jpg`,
    mimeType: params.mimeType || 'image/jpeg',
    width: Number(params.width),
    height: Number(params.height),
    type: 'image',
  };

  async function handleCreatePost() {
    if (!token) {
      setErrorMessage('You must be logged in to create a post.');
      return;
    }

    if (!params.imageUri) {
      setErrorMessage('The selected photo is missing.');
      return;
    }
    if (!requiresLocation && !coordinates) {
              setErrorMessage(
                'Your location must be available before creating the post.',
              );
              return;
            }

    try {
      setErrorMessage(null);
      setSubmissionStage('uploading');
      
      const uploadedImage = await uploadPostImage(
        authenticatedFetch,
        image
      );

      setSubmissionStage('creating');

      await createPost(authenticatedFetch, {
        image_url: uploadedImage.image_url,
        image_storage_path: uploadedImage.storage_path,
        brand: brand.trim() || null,
        model: model.trim() || null,
        ai_confidence: null,
        latitude:
          locationVisibility === 'private'
            ? null
            : coordinates?.latitude ?? null,

        longitude:
          locationVisibility === 'private'
            ? null
            : coordinates?.longitude ?? null,

        location_visibility: locationVisibility,
      });

      
      router.replace('/(tabs)');
    } catch (error) {
      console.error('[post] Could not create post:', error);
      setErrorMessage('Could not create the post.');
    } finally {
      setSubmissionStage('idle');
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.screen}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.title}>Create post</Text>

        <Text style={styles.subtitle}>
          Add some details about the spotted car
        </Text>

        <Image
          source={{ uri: params.imageUri }}
          style={styles.previewImage}
        />

        <Pressable
          style={styles.changePhotoButton}
          onPress={() => router.back()}
          disabled={isSubmitting}
        >
          <Text style={styles.changePhotoButtonText}>
            Change photo
          </Text>
        </Pressable>

        <View style={styles.field}>
          <Text style={styles.label}>Brand</Text>

          <TextInput
            value={brand}
            onChangeText={setBrand}
            placeholder="BMW"
            placeholderTextColor={AutoSpotColors.subtle}
            style={styles.input}
            editable={!isSubmitting}
          />
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Model</Text>

          <TextInput
            value={model}
            onChangeText={setModel}
            placeholder="M3"
            placeholderTextColor={AutoSpotColors.subtle}
            style={styles.input}
            editable={!isSubmitting}
          />
        </View>

      <View style={styles.visibilitySection}>
  <Text style={styles.label}>
    Location visibility
  </Text>

  <View style={styles.visibilityOptions}>
    {locationVisibilityOptions.map((option) => {
      const isSelected =
        locationVisibility === option.value;

      return (
        <Pressable
          key={option.value}
          style={[
            styles.visibilityOption,
            isSelected &&
              styles.selectedVisibilityOption,
          ]}
          disabled={isSubmitting}
          onPress={() => {
            setLocationVisibility(option.value);
          }}
        >
          <View style={styles.visibilityOptionHeader}>
            <View
              style={[
                styles.radioOuter,
                isSelected && styles.selectedRadioOuter,
              ]}
            >
              {isSelected ? (
                <View style={styles.radioInner} />
              ) : null}
            </View>

            <Text
              style={[
                styles.visibilityOptionTitle,
                isSelected &&
                  styles.selectedVisibilityOptionTitle,
              ]}
            >
              {option.title}
            </Text>
          </View>

          <Text style={styles.visibilityDescription}>
            {option.description}
          </Text>
        </Pressable>
      );
    })}
  </View>
</View>
    
        <View style={styles.locationCard}>
  <Text style={styles.locationTitle}>
    Location
  </Text>

  {locationStatus === 'loading' ? (
    <Text style={styles.locationLoadingText}>
      Getting your current location...
    </Text>
  ) : null}

  {locationStatus === 'ready' && coordinates ? (
    <>
      <Text style={styles.locationSuccessText}>
        {locationVisibility === 'private'
          ? 'Location hidden'
          : 'Location added'}
      </Text>

      <Text style={styles.locationPrivacyText}>
          {locationVisibility === 'approximate'
            ? 'Your position will be approximated before it appears on the map.'
            : locationVisibility === 'public'
              ? 'The saved position will be displayed directly on the map.'
              : 'The location will not be attached to this post.'}
      </Text>
    </>
  ) : null}

  {locationStatus === 'denied' ? (
    <>
      <Text style={styles.locationErrorText}>
        {locationError}
      </Text>

      {canAskAgain ? (
        <Pressable
          style={styles.locationButton}
          onPress={refreshLocation}
        >
          <Text style={styles.locationButtonText}>
            Allow location
          </Text>
        </Pressable>
      ) : (
        <Pressable
          style={styles.locationButton}
          onPress={() => Linking.openSettings()}
        >
          <Text style={styles.locationButtonText}>
            Open settings
          </Text>
        </Pressable>
      )}
    </>
  ) : null}

  {locationStatus === 'disabled' ? (
    <>
      <Text style={styles.locationErrorText}>
        Location services are disabled.
      </Text>

      <Pressable
        style={styles.locationButton}
        onPress={refreshLocation}
      >
        <Text style={styles.locationButtonText}>
          Try again
        </Text>
      </Pressable>
    </>
  ) : null}

  {locationStatus === 'error' ? (
    <>
      <Text style={styles.locationErrorText}>
        {locationError}
      </Text>

      <Pressable
        style={styles.locationButton}
        onPress={refreshLocation}
      >
        <Text style={styles.locationButtonText}>
          Try again
        </Text>
      </Pressable>
    </>
  ) : null}
</View>

        {errorMessage ? (
          <Text style={styles.errorText}>
            {errorMessage}
          </Text>
        ) : null}

        <Pressable
          style={[
            styles.submitButton,
            !canCreatePost && styles.disabledButton,
          ]}
          onPress={handleCreatePost}
          disabled={!canCreatePost}
        >
          <Text style={styles.submitButtonText}>
            {submitButtonText}
          </Text>
        </Pressable>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: AutoSpotColors.background,
  },

  content: {
    padding: 16,
    paddingTop: 56,
    paddingBottom: 40,
  },

  title: {
    color: AutoSpotColors.text,
    fontSize: 26,
    fontWeight: '800',
  },

  subtitle: {
    color: AutoSpotColors.muted,
    marginTop: 4,
    marginBottom: 20,
  },

  previewImage: {
    width: '100%',
    height: 280,
    borderRadius: 18,
    backgroundColor: AutoSpotColors.charcoal,
  },

  changePhotoButton: {
    alignSelf: 'flex-end',
    paddingVertical: 12,
  },

  changePhotoButtonText: {
    color: AutoSpotColors.primary,
    fontWeight: '700',
  },

  field: {
    marginBottom: 14,
  },

  label: {
    color: AutoSpotColors.text,
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
    marginBottom: 8,
  },

  input: {
    height: 48,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    borderRadius: 10,
    backgroundColor: AutoSpotColors.charcoal,
    color: AutoSpotColors.text,
    paddingHorizontal: 14,
    fontSize: 15,
  },

  submitButton: {
    marginTop: 10,
    height: 52,
    borderRadius: 14,
    backgroundColor: AutoSpotColors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },

  submitButtonText: {
    color: AutoSpotColors.text,
    fontSize: 16,
    fontWeight: '800',
  },

  disabledButton: {
    opacity: 0.6,
  },

  errorText: {
    color: AutoSpotColors.danger,
    marginBottom: 10,
    fontWeight: '700',
  },
  locationCard: {
  marginBottom: 18,
  padding: 16,
  borderRadius: 12,
  borderWidth: 1,
  borderColor: AutoSpotColors.border,
  backgroundColor: AutoSpotColors.charcoal,
},

locationTitle: {
  color: AutoSpotColors.text,
  fontSize: 12,
  fontWeight: '800',
  textTransform: 'uppercase',
  marginBottom: 8,
},

locationLoadingText: {
  color: AutoSpotColors.muted,
},

locationSuccessText: {
  color: AutoSpotColors.primary,
  fontWeight: '800',
},

locationPrivacyText: {
  color: AutoSpotColors.muted,
  fontSize: 12,
  marginTop: 6,
},

locationErrorText: {
  color: AutoSpotColors.danger,
  fontWeight: '700',
},

locationButton: {
  alignSelf: 'flex-start',
  marginTop: 12,
  minHeight: 42,
  paddingHorizontal: 16,
  borderRadius: 10,
  backgroundColor: AutoSpotColors.primary,
  alignItems: 'center',
  justifyContent: 'center',
},

locationButtonText: {
  color: AutoSpotColors.text,
  fontWeight: '800',
},
visibilitySection: {
  marginBottom: 18,
},

visibilityOptions: {
  gap: 10,
},

visibilityOption: {
  padding: 14,
  borderRadius: 12,
  borderWidth: 1,
  borderColor: AutoSpotColors.border,
  backgroundColor: AutoSpotColors.charcoal,
},

selectedVisibilityOption: {
  borderColor: AutoSpotColors.primary,
  backgroundColor: AutoSpotColors.card,
},

visibilityOptionHeader: {
  flexDirection: 'row',
  alignItems: 'center',
  gap: 10,
},

radioOuter: {
  width: 20,
  height: 20,
  borderRadius: 10,
  borderWidth: 2,
  borderColor: AutoSpotColors.subtle,
  alignItems: 'center',
  justifyContent: 'center',
},

selectedRadioOuter: {
  borderColor: AutoSpotColors.primary,
},

radioInner: {
  width: 10,
  height: 10,
  borderRadius: 5,
  backgroundColor: AutoSpotColors.primary,
},

visibilityOptionTitle: {
  color: AutoSpotColors.text,
  fontSize: 15,
  fontWeight: '700',
},

selectedVisibilityOptionTitle: {
  color: AutoSpotColors.primary,
},

visibilityDescription: {
  color: AutoSpotColors.muted,
  fontSize: 12,
  lineHeight: 18,
  marginTop: 8,
  marginLeft: 30,
},
});