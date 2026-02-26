import { StyleSheet, Text, View } from 'react-native';

export default function SwingsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>SwingLens</Text>
      <View style={styles.accent} />
      <Text style={styles.subtitle}>Your swings will appear here</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0a0f0d',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#34d399',
  },
  accent: {
    width: 48,
    height: 3,
    backgroundColor: '#34d399',
    borderRadius: 2,
    marginVertical: 12,
  },
  subtitle: {
    fontSize: 16,
    color: '#9ca3af',
  },
});
