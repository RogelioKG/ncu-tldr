import type { AuthUser } from '@/api/auth'

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { getMe, login, logoutApi, register } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const isLoading = ref(false)
  const isInitialized = ref(false)

  let _hydrationPromise: Promise<void> | null = null

  const isLoggedIn = computed(() => user.value !== null)
  const displayName = computed(() => user.value?.displayName ?? '')

  async function loginWithPassword(email: string, password: string, rememberMe = false): Promise<void> {
    isLoading.value = true
    try {
      user.value = await login({ email, password, rememberMe })
    }
    finally {
      isLoading.value = false
    }
  }

  async function registerWithPassword(
    email: string,
    password: string,
    displayNameValue: string,
  ): Promise<void> {
    isLoading.value = true
    try {
      await register({ email, password, displayName: displayNameValue })
    }
    finally {
      isLoading.value = false
    }
  }

  function hydrateFromStorage(): Promise<void> {
    if (_hydrationPromise)
      return _hydrationPromise
    _hydrationPromise = getMe()
      .then((me) => { user.value = me })
      .catch(() => { user.value = null })
      .finally(() => { isInitialized.value = true })
    return _hydrationPromise
  }

  async function logout(): Promise<void> {
    try {
      await logoutApi()
    }
    catch {
      // ignore — clear local state regardless
    }
    user.value = null
  }

  return {
    displayName,
    hydrateFromStorage,
    isInitialized,
    isLoading,
    isLoggedIn,
    loginWithPassword,
    logout,
    registerWithPassword,
    user,
  }
})
