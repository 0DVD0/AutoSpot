import Ionicons from '@expo/vector-icons/Ionicons';
import { Pressable, StyleSheet, Text, View, TextInput } from 'react-native';
import { router } from 'expo-router';
import { useState } from 'react';
import { createPost } from '@/services/api';
import { useAuth } from '@/context/AuthContext';
import { AutoSpotColors } from '@/constants/autospotTheme';
import { useAuthenticatedApi } from '@/hooks/useAuthenticatedApi';

export default function PostScreen() {
  const { token } = useAuth();
  const { authenticatedFetch } = useAuthenticatedApi();

  const [imageUrl, setImageUrl] = useState('');
  const [brand, setBrand] = useState('');
  const [model, setModel] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  async function handleCreatePost() {
    if (!token) {
      setErrorMessage('You must be logged in to create a post.')
      return;
    }

    try {
      setErrorMessage(null);
      setIsSubmitting(true);
      await createPost(authenticatedFetch, {
      image_url: imageUrl,
      brand: brand || null,
      model: model || null,
      ai_confidence: null,
      latitude: latitude ? Number(latitude) : null,
      longitude: longitude ? Number(longitude) : null,
      location_visibility: 'public',      } );

      setImageUrl('');
      setBrand('');
      setModel('');
      setLatitude('');
      setLongitude('');

      router.replace('/(tabs)');
    } catch {
      setErrorMessage('Could not create post.');
    } finally {
      setIsSubmitting(false);
      }
  }
  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Spot a Car</Text>
      <Text style={styles.subtitle}>Capture an interesting car and create a live post</Text>

      <View style={styles.cameraBox}>
        <Ionicons name="camera" size={72} color={AutoSpotColors.primary} />
        <Text style={styles.cameraText}>Camera flow placeholder</Text>
      </View>
      
      {errorMessage && <Text style={styles.errorText}>{errorMessage}</Text>}
      <Pressable style={[styles.button, isSubmitting && styles.disabledButton]} onPress={handleCreatePost} disabled={isSubmitting}>
        <Text style={styles.buttonText}>{isSubmitting ? 'Creating post...': 'Create Post'}</Text>
      </Pressable>

      <View style={styles.field}>
        <Text style={styles.label}>Img_URL</Text>
        <TextInput value={imageUrl} onChangeText={setImageUrl} placeholder="Img_URL" placeholderTextColor={AutoSpotColors.subtle} style={styles.input}/> 
      </View>

      <View style={styles.field}>
        <Text style={styles.label}>Brand</Text>
        <TextInput value={brand} onChangeText={setBrand} placeholder="brand" placeholderTextColor={AutoSpotColors.subtle} style={styles.input}/> 
      </View>

      <View style={styles.field}>
        <Text style={styles.label}>Model</Text>
        <TextInput value={model} onChangeText={setModel} placeholder="Model" placeholderTextColor={AutoSpotColors.subtle} style={styles.input}/> 
      </View>

      <View style={styles.field}>
        <Text style={styles.label}>Lat</Text>
        <TextInput value={latitude} onChangeText={setLatitude} placeholder="Lat" placeholderTextColor={AutoSpotColors.subtle} style={styles.input} keyboardType="numeric"/> 
      </View>

      <View style={styles.field}>
        <Text style={styles.label}>Long</Text>
        <TextInput value={longitude} onChangeText={setLongitude} placeholder="Long" placeholderTextColor={AutoSpotColors.subtle} style={styles.input} keyboardType="numeric"/> 
        
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: AutoSpotColors.background,
    padding: 16,
    paddingTop: 56,
  },
  title: {
    color: AutoSpotColors.text,
    fontSize: 26,
    fontWeight: '800',
  },
  subtitle: {
    color: AutoSpotColors.muted,
    marginTop: 4,
    marginBottom: 24,
  },
  cameraBox: {
    height: 160,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    backgroundColor: AutoSpotColors.charcoal,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cameraText: {
    color: AutoSpotColors.muted,
    marginTop: 12,
  },
  button: {
    marginTop: 20,
    height: 52,
    borderRadius: 14,
    backgroundColor: AutoSpotColors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: AutoSpotColors.text,
    fontSize: 16,
    fontWeight: '800',
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
disabledButton: {
  opacity: 0.65,
},

errorText: {
  color: AutoSpotColors.danger,
  marginTop: 8,
  marginBottom: 8,
  fontWeight: '700',
},
});
