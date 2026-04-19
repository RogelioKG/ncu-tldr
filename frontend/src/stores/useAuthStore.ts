import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getMe, login, logoutApi, register } from '@/api/auth'

interface AuthUser {
  id: string
  email: string
  displayName: string
  isActive: boolean
  emailVerified: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const isLoading = ref(false)

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

  async function hydrateFromStorage(): Promise<void> {
    try {
      user.value = await getMe()
    }
    catch {
      user.value = null
    }
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
    isLoading,
    isLoggedIn,
    loginWithPassword,
    logout,
    registerWithPassword,
    user,
  }
})
