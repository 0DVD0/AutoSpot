import { AuthenticatedFetch } from "@/hooks/useAuthenticatedApi";
import { ImagePickerAsset } from "expo-image-picker";
import { API_BASE_URL } from "./api";


export type UploadResult = {
    image_url: string;
    storage_path: string;
}

export async function uploadPostImage(authentificatedFetch: AuthenticatedFetch, image: ImagePickerAsset): Promise<UploadResult> {
    
    const formData = new FormData();

    const mimeType = image.mimeType ?? 'image/jpeg'

    const extention = mimeType === 'image/png' ? 'png' : mimeType === 'image/webp' ? 'webp' : 'jpg'

    const fileName = image.fileName ?? `autospot-${Date.now()}.${extention}`

    formData.append('file', 
    {
        uri: image.uri,
        name: fileName,
        type: mimeType
    } as any )

    const response = await authentificatedFetch(
        `${API_BASE_URL}/uploads/upload-image`,
        {
            method: 'POST',
            body: formData
        }
    )

    if (!response.ok){
        throw new Error('Could not upload image')
    }

    return response.json();
}