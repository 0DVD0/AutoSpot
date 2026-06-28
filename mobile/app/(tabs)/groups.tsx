import { FlatList, StyleSheet, Text, View } from 'react-native';

import { AutoSpotColors } from '@/constants/autospotTheme';

const groups = ['BMW Enthusiasts', 'Porsche Owners', 'JDM Legends', 'Classic Cars', 'Electric Cars'];

export default function GroupsScreen() {
  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Groups</Text>
      <Text style={styles.subtitle}>Join communities around brands and car culture</Text>

      <FlatList
        data={groups}
        keyExtractor={(item) => item}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.groupName}>{item}</Text>
            <Text style={styles.groupMeta}>Community discussions and car spots</Text>
          </View>
        )}
      />
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
  list: {
    gap: 12,
    paddingBottom: 120,
  },
  card: {
    backgroundColor: AutoSpotColors.charcoal,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    padding: 16,
  },
  groupName: {
    color: AutoSpotColors.text,
    fontSize: 17,
    fontWeight: '800',
  },
  groupMeta: {
    color: AutoSpotColors.muted,
    marginTop: 4,
  },
});