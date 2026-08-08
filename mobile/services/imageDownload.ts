import { File, Paths } from 'expo-file-system';
import * as MediaLibrary from 'expo-media-library';


export async function downloadImageToLibrary(
  imageUrl: string
): Promise<void> {
  console.log('[download] Checking permission');

  let permission = await MediaLibrary.getPermissionsAsync(true);

  console.log('[download] Current permission:', permission);

  if (!permission.granted) {
    if (!permission.canAskAgain) {
      throw new Error(
        'Photos permission is disabled. Enable it from iPhone Settings.'
      );
    }

    console.log('[download] Requesting permission');

    permission = await MediaLibrary.requestPermissionsAsync(true);

    console.log('[download] Requested permission result:', permission);
  }

  if (!permission.granted) {
    throw new Error('Permission to save photos was denied.');
  }

  const destinationFile = new File(
    Paths.cache,
    `autospot-${Date.now()}.jpg`
  );

  console.log('[download] Downloading image');

  const downloadedFile = await File.downloadFileAsync(
    imageUrl,
    destinationFile
  );

  console.log('[download] Downloaded:', {
    uri: downloadedFile.uri,
    exists: downloadedFile.exists,
  });

  if (!downloadedFile.exists) {
    throw new Error('The downloaded image does not exist.');
  }

  console.log('[download] Saving to Photos');

  await MediaLibrary.saveToLibraryAsync(downloadedFile.uri);

  console.log('[download] Image saved');
}