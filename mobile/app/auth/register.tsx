import Ionicons from '@expo/vector-icons/Ionicons';
import { Link, router } from 'expo-router';
import { useState } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { AutoSpotColors } from '@/constants/autospotTheme';
import { registerRequest } from '@/services/authAPI';

export default function RegisterScreen() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const passwordStrength =
    password.length === 0 ? 0 : password.length < 6 ? 1 : password.length < 10 ? 2 : 3;

  const strengthLabel = ['', 'Weak', 'Good', 'Strong'][passwordStrength];

  async function handleRegister() {
    if (password !== confirm) {
      setErrorMessage('Passwords do not match.');
      return;
    }

    try {
      setErrorMessage(null);
      setIsSubmitting(true);

      await registerRequest({
        username,
        email,
        password,
        avatar_url: null,
        bio: null,
      });

      router.replace('/auth/login');
    } catch {
      setErrorMessage('Could not create account.');
    } finally {
      setIsSubmitting(false);
    }
  }
  function getStrengthStyle() {
  if (passwordStrength === 1) {
    return styles.strength1;
  }

  if (passwordStrength === 2) {
    return styles.strength2;
  }

  if (passwordStrength === 3) {
    return styles.strength3;
  }

  return null;
}
  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <Pressable style={styles.backButton} onPress={() => router.replace('/auth/login')}>
          <Ionicons name="chevron-back" size={24} color={AutoSpotColors.text} />
        </Pressable>

        <View>
          <Text style={styles.headerTitle}>Create Account</Text>
          <Text style={styles.headerSubtitle}>Join the AutoSpot community</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.infoBox}>
          {[
            'Temporary posts vanish after 24 hours',
            'Locations can be approximate',
            'Community-driven car culture',
          ].map((item) => (
            <View key={item} style={styles.infoRow}>
              <View style={styles.checkCircle}>
                <Ionicons name="checkmark" size={12} color={AutoSpotColors.primary} />
              </View>
              <Text style={styles.infoText}>{item}</Text>
            </View>
          ))}
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Username</Text>
          <View style={styles.inputWrap}>
            <Ionicons name="person" size={18} color={AutoSpotColors.subtle} />
            <TextInput
              value={username}
              onChangeText={setUsername}
              placeholder="spotter_name"
              placeholderTextColor={AutoSpotColors.subtle}
              autoCapitalize="none"
              style={styles.input}
            />
          </View>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Email</Text>
          <View style={styles.inputWrap}>
            <Ionicons name="mail" size={18} color={AutoSpotColors.subtle} />
            <TextInput
              value={email}
              onChangeText={setEmail}
              placeholder="you@example.com"
              placeholderTextColor={AutoSpotColors.subtle}
              keyboardType="email-address"
              autoCapitalize="none"
              style={styles.input}
            />
          </View>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Password</Text>
          <View style={styles.inputWrap}>
            <Ionicons name="lock-closed" size={18} color={AutoSpotColors.subtle} />
            <TextInput
              value={password}
              onChangeText={setPassword}
              placeholder="Min. 6 characters"
              placeholderTextColor={AutoSpotColors.subtle}
              secureTextEntry={!showPassword}
              style={styles.input}
            />
            <Pressable onPress={() => setShowPassword((value) => !value)}>
              <Ionicons
                name={showPassword ? 'eye-off' : 'eye'}
                size={20}
                color={AutoSpotColors.muted}
              />
            </Pressable>
          </View>

          {password.length > 0 && (
            <View style={styles.strengthRow}>
              {[1, 2, 3].map((level) => (
                <View
                  key={level}
                  style={[
                    styles.strengthBar,
                    passwordStrength >= level && getStrengthStyle(),
                  ]}
                />
              ))}
              <Text style={styles.strengthText}>{strengthLabel}</Text>
            </View>
          )}
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Confirm Password</Text>
          <View
            style={[
              styles.inputWrap,
              confirm.length > 0 && confirm !== password && styles.inputError,
            ]}
          >
            <Ionicons name="lock-closed" size={18} color={AutoSpotColors.subtle} />
            <TextInput
              value={confirm}
              onChangeText={setConfirm}
              placeholder="Repeat password"
              placeholderTextColor={AutoSpotColors.subtle}
              secureTextEntry={!showConfirm}
              style={styles.input}
            />
            <Pressable onPress={() => setShowConfirm((value) => !value)}>
              <Ionicons
                name={showConfirm ? 'eye-off' : 'eye'}
                size={20}
                color={AutoSpotColors.muted}
              />
            </Pressable>
          </View>

          {confirm.length > 0 && confirm !== password && (
            <Text style={styles.errorSmall}>Passwords do not match</Text>
          )}
        </View>

        <Text style={styles.terms}>
          By creating an account you agree to our Terms of Service and Privacy Policy.
        </Text>

        {errorMessage && <Text style={styles.error}>{errorMessage}</Text>}

        <Pressable
          style={[styles.primaryButton, isSubmitting && styles.disabledButton]}
          onPress={handleRegister}
          disabled={isSubmitting}
        >
          <Text style={styles.primaryButtonText}>
            {isSubmitting ? 'Creating...' : 'Create Account'}
          </Text>
          <Ionicons name="arrow-forward" size={18} color={AutoSpotColors.text} />
        </Pressable>

        <Text style={styles.bottomText}>
          Already have an account?{' '}
          <Link href="/auth/login" style={styles.link}>
            Sign in
          </Link>
        </Text>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: AutoSpotColors.background,
  },
  header: {
    paddingTop: 56,
    paddingHorizontal: 18,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: AutoSpotColors.border,
    backgroundColor: AutoSpotColors.charcoal,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: AutoSpotColors.card,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    color: AutoSpotColors.text,
    fontSize: 20,
    fontWeight: '900',
  },
  headerSubtitle: {
    color: AutoSpotColors.muted,
    marginTop: 2,
    fontSize: 12,
  },
  content: {
    padding: 24,
    paddingBottom: 44,
  },
  infoBox: {
    borderWidth: 1,
    borderColor: 'rgba(14, 165, 233, 0.25)',
    backgroundColor: 'rgba(14, 165, 233, 0.06)',
    borderRadius: 14,
    padding: 14,
    gap: 8,
    marginBottom: 24,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  checkCircle: {
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: 'rgba(14, 165, 233, 0.16)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  infoText: {
    color: AutoSpotColors.muted,
    fontSize: 13,
  },
  field: {
    marginBottom: 16,
  },
  label: {
    color: AutoSpotColors.text,
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
    marginBottom: 8,
  },
  inputWrap: {
    height: 52,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    borderRadius: 10,
    backgroundColor: AutoSpotColors.charcoal,
    paddingHorizontal: 14,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  inputError: {
    borderColor: AutoSpotColors.danger,
  },
  input: {
    flex: 1,
    color: AutoSpotColors.text,
    fontSize: 15,
  },
  strengthRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 8,
  },
  strengthBar: {
    flex: 1,
    height: 4,
    borderRadius: 2,
    backgroundColor: AutoSpotColors.border,
  },
  strength1: {
    backgroundColor: AutoSpotColors.danger,
  },
  strength2: {
    backgroundColor: AutoSpotColors.amber,
  },
  strength3: {
    backgroundColor: '#22c55e',
  },
  strengthText: {
    color: AutoSpotColors.muted,
    fontSize: 12,
    width: 44,
    textAlign: 'right',
  },
  errorSmall: {
    color: AutoSpotColors.danger,
    marginTop: 6,
    fontSize: 12,
    fontWeight: '700',
  },
  terms: {
    color: AutoSpotColors.subtle,
    fontSize: 12,
    lineHeight: 18,
    marginBottom: 16,
  },
  error: {
    color: AutoSpotColors.danger,
    marginBottom: 12,
    fontWeight: '700',
  },
  primaryButton: {
    height: 52,
    borderRadius: 10,
    backgroundColor: AutoSpotColors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    gap: 8,
  },
  disabledButton: {
    opacity: 0.65,
  },
  primaryButtonText: {
    color: AutoSpotColors.text,
    fontWeight: '900',
    textTransform: 'uppercase',
  },
  bottomText: {
    color: AutoSpotColors.muted,
    textAlign: 'center',
    marginTop: 28,
  },
  link: {
    color: AutoSpotColors.primary,
    fontWeight: '800',
  },
});