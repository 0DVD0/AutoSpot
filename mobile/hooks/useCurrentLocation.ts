import { useCallback, useEffect, useState } from "react";
import * as Location from "expo-location"

export type CurrentCoordinates = {
    latitude: number;
    longitude: number;
}

export type LocationLoadingStatus = 
| 'loading'
| 'ready'
| 'denied'
| 'disabled'
| 'error'

export function useCurrentLocation() {
    const [coordinates, setCoordinates] = useState<CurrentCoordinates | null>(null)
    const [errorMessage, setErrorMessage] = useState<string | null>(null)
    const [status, setStatus] = useState<LocationLoadingStatus>('loading')
    const [canAskAgain, setCanAskAgain] = useState(true)
    const refreshLocation = useCallback(async () => {
        try {
            setStatus('loading')
            setErrorMessage(null)

            const servicesEnabled = await Location.hasServicesEnabledAsync();

            if (!servicesEnabled) {
                setCoordinates(null)
                setStatus('disabled')
                setErrorMessage('Location has been disabled on this device')
                return
            }

            let permission = await Location.getForegroundPermissionsAsync();

            if (!permission.granted && permission.canAskAgain){
                permission = await Location.requestForegroundPermissionsAsync()
            }

            setCanAskAgain(permission.canAskAgain)

            if (!permission.granted){
                setCoordinates(null)
                setStatus('denied')
                setErrorMessage('Location permission required')
                return
            } 
            const currentPosition = await Location.getCurrentPositionAsync(
                {
                    accuracy: Location.Accuracy.Balanced
                }
            )

            setCoordinates({
                latitude: currentPosition.coords.latitude,
                longitude: currentPosition.coords.longitude
            })

            setStatus('ready')
        } catch (error) {
            console.error(
                '[location] Could not get current location', error
            )
            setCoordinates(null)
            setStatus('error')
            setErrorMessage('Could not determine your current location')
        }
}, [])

    useEffect(() => {
        void refreshLocation()
    }, [refreshLocation])

    return {
        coordinates, status, errorMessage, canAskAgain, refreshLocation
    }
}   