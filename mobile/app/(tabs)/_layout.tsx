import Ionicons from '@expo/vector-icons/Ionicons';
import { Tabs, Redirect } from 'expo-router';
import React from 'react';
import { useAuth } from '@/context/AuthContext';

import { AutoSpotColors } from '@/constants/autospotTheme';

export default function TabLayout() {
  const { token, isLoading } = useAuth();

if (isLoading) {
  return null;
}

if (!token) {
  return <Redirect href="/auth/login" />;
}
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: AutoSpotColors.primary,
        tabBarInactiveTintColor: AutoSpotColors.subtle,
        tabBarStyle: {
          backgroundColor: AutoSpotColors.charcoal,
          borderTopColor: AutoSpotColors.border,
          height: 76,
          paddingTop: 8,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '700',
        },
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home" size={size} color={color} />
          ),
        }}
      />

      <Tabs.Screen
        name="explore"
        options={{
          title: 'Explore',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="map" size={size} color={color} />
          ),
        }}
      />

      <Tabs.Screen
        name="post"
        options={{
          title: 'Post',
          tabBarIcon: ({ color, size }) => (
            <Ionicons
              name="camera"
              size={size}
              color={color}
            />
          ),
        }}
      />

      <Tabs.Screen
        name="groups"
        options={{
          title: 'Groups',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="people" size={size} color={color} />
          ),
        }}
      />

      <Tabs.Screen
        name="account"
        options={{
          title: 'Account',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="person-circle" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}