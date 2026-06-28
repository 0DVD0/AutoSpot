import Ionicons from '@expo/vector-icons/Ionicons';
import { Link, router } from 'expo-router';
import { useState } from 'react';
import {
  ImageBackground,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { AutoSpotColors } from '@/constants/autospotTheme';
import { useAuth } from '@/context/AuthContext';

export default function LoginScreen() {
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleLogin() {
    try {
      setErrorMessage(null);
      setIsSubmitting(true);

      await login({ email, password });

      router.replace('/(tabs)');
    } catch {
      setErrorMessage('Invalid email or password.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <View style={styles.screen}>
      <ImageBackground
        source={{
          uri: 'https://images.unsplash.com/photo-1583121274602-3e2820c69888?w=1200&q=80',
        }}
        style={styles.hero}
        imageStyle={styles.heroImage}
      >
        <View style={styles.heroOverlay}>
          <View style={styles.logoBox}>
            <Text style={styles.logoInitials}>AS</Text>
          </View>

          <Text style={styles.logo}>AutoSpot</Text>
          <Text style={styles.tagline}>Spot. Share. Connect.</Text>
        </View>
      </ImageBackground>

      <View style={styles.form}>
        <Text style={styles.title}>Welcome back</Text>
        <Text style={styles.subtitle}>Sign in to continue spotting</Text>

        <View style={styles.field}>
          <Text style={styles.label}>Email</Text>

          <View style={styles.inputWrap}>
            <Ionicons name="mail" size={18} color={AutoSpotColors.subtle} />
            <TextInput
              value={email}
              onChangeText={setEmail}
              placeholder="you@example.com"
              placeholderTextColor={AutoSpotColors.subtle}
              autoCapitalize="none"
              keyboardType="email-address"
              style={styles.input}
            />
          </View>
        </View>

        <View style={styles.field}>
          <View style={styles.passwordLabelRow}>
            <Text style={styles.label}>Password</Text>
            <Text style={styles.forgot}>Forgot password?</Text>
          </View>

          <View style={styles.inputWrap}>
            <Ionicons name="lock-closed" size={18} color={AutoSpotColors.subtle} />

            <TextInput
              value={password}
              onChangeText={setPassword}
              placeholder="Password"
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
        </View>

        {errorMessage && <Text style={styles.error}>{errorMessage}</Text>}

        <Pressable
          style={[styles.primaryButton, isSubmitting && styles.disabledButton]}
          onPress={handleLogin}
          disabled={isSubmitting}
        >
          <Text style={styles.primaryButtonText}>
            {isSubmitting ? 'Signing in...' : 'Sign In'}
          </Text>
          <Ionicons name="arrow-forward" size={18} color={AutoSpotColors.text} />
        </Pressable>

        <View style={styles.dividerRow}>
          <View style={styles.divider} />
          <Text style={styles.dividerText}>or</Text>
          <View style={styles.divider} />
        </View>

        <View style={styles.socialRow}>
          <Pressable style={styles.socialButton}>
            <Text style={styles.socialText}>Google</Text>
          </Pressable>

          <Pressable style={styles.socialButton}>
            <Text style={styles.socialText}>Apple</Text>
          </Pressable>
        </View>

        <Text style={styles.bottomText}>
          Don&apos;t have an account?{' '}
          <Link href="/auth/register" style={styles.link}>
            Create one
          </Link>
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: AutoSpotColors.background,
  },
  hero: {
    height: 230,
  },
  heroImage: {
    resizeMode: 'cover',
  },
  heroOverlay: {
    flex: 1,
    backgroundColor: 'rgba(10, 10, 15, 0.55)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoBox: {
    width: 56,
    height: 56,
    borderRadius: 16,
    backgroundColor: 'rgba(14, 165, 233, 0.18)',
    borderWidth: 1,
    borderColor: 'rgba(14, 165, 233, 0.45)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  logoInitials: {
    color: AutoSpotColors.text,
    fontSize: 22,
    fontWeight: '900',
  },
  logo: {
    color: AutoSpotColors.text,
    fontSize: 28,
    fontWeight: '900',
  },
  tagline: {
    color: AutoSpotColors.muted,
    marginTop: 4,
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  form: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 28,
  },
  title: {
    color: AutoSpotColors.text,
    fontSize: 26,
    fontWeight: '800',
  },
  subtitle: {
    color: AutoSpotColors.muted,
    marginTop: 4,
    marginBottom: 28,
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
  passwordLabelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  forgot: {
    color: AutoSpotColors.primary,
    fontSize: 12,
    fontWeight: '700',
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
  input: {
    flex: 1,
    color: AutoSpotColors.text,
    fontSize: 15,
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
    marginTop: 4,
  },
  disabledButton: {
    opacity: 0.65,
  },
  primaryButtonText: {
    color: AutoSpotColors.text,
    fontWeight: '900',
    textTransform: 'uppercase',
  },
  dividerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginVertical: 24,
  },
  divider: {
    flex: 1,
    height: 1,
    backgroundColor: AutoSpotColors.border,
  },
  dividerText: {
    color: AutoSpotColors.subtle,
    fontSize: 12,
    textTransform: 'uppercase',
  },
  socialRow: {
    flexDirection: 'row',
    gap: 12,
  },
  socialButton: {
    flex: 1,
    height: 46,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    backgroundColor: AutoSpotColors.charcoal,
    alignItems: 'center',
    justifyContent: 'center',
  },
  socialText: {
    color: AutoSpotColors.text,
    fontWeight: '700',
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