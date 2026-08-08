import Ionicons from '@expo/vector-icons/Ionicons';
import { Pressable, StyleSheet, Text, View} from 'react-native';
import { router } from 'expo-router';
import { useEffect, useRef, useState } from 'react';
import { AutoSpotColors } from '@/constants/autospotTheme';
import * as ImagePicker from 'expo-image-picker';
import {CameraType, CameraView, useCameraPermissions} from 'expo-camera'
import { useIsFocused } from '@react-navigation/native';

export default function PostScreen() {
  const cameraRef = useRef<CameraView | null>(null);
  const [facing, setFacing] = useState<CameraType>('back');
  const [permission, requestPermission] = useCameraPermissions();
  const [isCameraReady, setCameraReady] = useState(false);
  const [isTakingPhoto, setIsTakingPhoto] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const isFocused = useIsFocused();
  
  useEffect(() => {
    if (!isFocused) {
      setCameraReady(false);
    }
  }, [isFocused]);
  function openPostForm(asset: ImagePicker.ImagePickerAsset) {
      router.push({
    pathname: "/post/postForm",
    params: {
      imageUri: asset.uri,
      fileName: asset.fileName ?? '',
      mimeType: asset.mimeType ?? 'image/jpeg',
      width: String(asset.width),
      height: String(asset.height),
    },
});
  }
  async function takePhoto() {
    if (!cameraRef.current || !isCameraReady || isTakingPhoto){
      return;
    }
    try {
      setIsTakingPhoto(true);
      setErrorMessage(null);

      const photo = await cameraRef.current.takePictureAsync({quality: 0.8})

      const asset: ImagePicker.ImagePickerAsset= {
        uri: photo.uri,
        width: photo.width,
        height: photo.height,
        fileName: `autospot-${Date.now()}.jpg`,
        mimeType: 'image/jpeg',
        type: 'image'
      }

      openPostForm(asset)
    } catch (error){
      console.error('[camera] Could not take photo:', error)
      setErrorMessage('Could not take photo')
    } finally {
      setIsTakingPhoto(false);
    }
  }

   function toggleCamera() {
    setFacing((current) => {
      return current === 'back' ? 'front': 'back'
    })
  }
    async function pickImage() {
      try{
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        quality: 0.8,
      })

      if (!result.canceled && result.assets.length > 0) {
        openPostForm(result.assets[0]);
      }
      } catch (error){
        console.error('[gallery] Could not be open');
        setErrorMessage('Could not load image from gallery')
      };
    }

    
    if (!permission){
      return (
        <View style={styles.permissionScreen}>
          <Text style={styles.permissionText}>
            Checking camera...
          </Text>
        </View>
      )
    }

    if (!permission.granted){
      return (
        <View style={styles.permissionScreen}>
      <Ionicons
        name="camera-outline"
        size={72}
        color={AutoSpotColors.primary}
      />

      <Text style={styles.permissionTitle}>
        Camera permission required
      </Text>

      <Text style={styles.permissionText}>
        AutoSpot needs camera access so you can photograph spotted cars.
      </Text>

      <Pressable
        style={styles.permissionButton}
        onPress={requestPermission}
      >
        <Text style={styles.permissionButtonText}>
          Allow camera
        </Text>
      </Pressable>
    </View>
      )
    }
  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Spot a Car</Text>
      <Text style={styles.subtitle}>Capture an interesting car and create a live post</Text>

      <View style={styles.cameraContainer}>
       {isFocused ? (
          <CameraView
            ref={cameraRef}
            style={styles.camera}
            facing={facing}
            mode="picture"
            onCameraReady={() => setCameraReady(true)}
            onMountError={(event) => {
              console.error('[camera] Mount error:', event.message);
              setErrorMessage('Could not start the camera.');
            }}
          />
        ) : (
          <View style={styles.cameraInactive} />
        )}
      </View>

      {errorMessage ? (
        <Text style={styles.errorText}>
          {errorMessage}
        </Text>
      ) : null}

      <View style={styles.cameraControls}>
        {/*
         * Butonul din stânga deschide galeria.
         */}
        <Pressable
          style={styles.controlButton}
          onPress={pickImage}
          disabled={isTakingPhoto}
        >
          <Ionicons
            name="images-outline"
            size={28}
            color={AutoSpotColors.text}
          />
        </Pressable>

        {/*
         * Butonul central realizează fotografia.
         */}
        <Pressable
          style={[
            styles.captureButton,
            (!isCameraReady || isTakingPhoto) && styles.disabledButton,
          ]}
          onPress={takePhoto}
          disabled={!isCameraReady || isTakingPhoto}
        >
          <View style={styles.captureButtonInner} />
        </Pressable>

        {/*
         * Butonul din dreapta schimbă camera.
         */}
        <Pressable
          style={styles.controlButton}
          onPress={toggleCamera}
          disabled={isTakingPhoto}
        >
          <Ionicons
            name="camera-reverse-outline"
            size={28}
            color={AutoSpotColors.text}
          />
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: AutoSpotColors.background,
    paddingHorizontal: 16,
    paddingTop: 56,
    paddingBottom: 12,
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

  cameraContainer: {
    flex: 1,
    overflow: 'hidden',
    borderRadius: 20,
    backgroundColor: '#000000',
  },

  camera: {
    flex: 1,
  },

  cameraInactive: {
    flex: 1,
    backgroundColor: '#000000',
  },

  cameraControls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingTop: 18,
  },

  controlButton: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: AutoSpotColors.charcoal,
    alignItems: 'center',
    justifyContent: 'center',
  },

  captureButton: {
    width: 76,
    height: 76,
    borderRadius: 38,
    borderWidth: 4,
    borderColor: AutoSpotColors.text,
    alignItems: 'center',
    justifyContent: 'center',
  },

  captureButtonInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: AutoSpotColors.primary,
  },

  disabledButton: {
    opacity: 0.5,
  },

  errorText: {
    color: AutoSpotColors.danger,
    marginTop: 10,
    textAlign: 'center',
    fontWeight: '700',
  },

  permissionScreen: {
    flex: 1,
    padding: 24,
    backgroundColor: AutoSpotColors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },

  permissionTitle: {
    marginTop: 20,
    color: AutoSpotColors.text,
    fontSize: 22,
    fontWeight: '800',
  },

  permissionText: {
    marginTop: 12,
    color: AutoSpotColors.muted,
    textAlign: 'center',
  },

  permissionButton: {
    marginTop: 24,
    paddingHorizontal: 24,
    height: 50,
    borderRadius: 14,
    backgroundColor: AutoSpotColors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },

  permissionButtonText: {
    color: AutoSpotColors.text,
    fontSize: 16,
    fontWeight: '800',
  },
});
