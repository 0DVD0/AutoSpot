import { StyleSheet, Text, View } from 'react-native';

import { AutoSpotColors } from '@/constants/autospotTheme';

export default function ExploreScreen() {
  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Explore</Text>
      <Text style={styles.subtitle}>Map of live car spots around your region</Text>

      <View style={styles.mapPlaceholder}>
        <Text style={styles.mapText}>Map preview</Text>
        <Text style={styles.mapHint}>Markers will appear here later</Text>
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
    marginBottom: 20,
  },
  mapPlaceholder: {
    flex: 1,
    borderRadius: 18,
    backgroundColor: AutoSpotColors.charcoal,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  mapText: {
    color: AutoSpotColors.primary,
    fontSize: 22,
    fontWeight: '800',
  },
  mapHint: {
    color: AutoSpotColors.muted,
    marginTop: 8,
  },
});