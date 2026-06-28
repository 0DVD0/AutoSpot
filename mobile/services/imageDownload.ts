import { File, Paths } from 'expo-file-system';
import { Asset, requestPermissionsAsync } from 'expo-media-library/next';

export async function downloadImageToLibrary(image_url: string) {
    const permission = await requestPermissionsAsync();

    if (!permission.granted){
        throw new Error('Permission to gallery was denied')
    }
    
    const fileName = `autospot-${Date.now()}.jpg`;
    const destinationFile = new File(Paths.cache, fileName);

    const downloadResult = await File.downloadFileAsync(
        image_url,
        destinationFile
    );

    const asset = await Asset.create(downloadResult.uri);

    return asset
}