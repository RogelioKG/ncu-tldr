import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getMe, login, register } from '@/api/auth'

const AUTH_TOKEN_KEY = 'ncu-tldr-token'

interface AuthUser {
  id: string
  email: string
  displayName: string
  isActive: boolean
  emailVerified: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(AUTH_TOKEN_KEY))
  const user = ref<AuthUser | null>(null)
  const isLoading = ref(false)

  const isLoggedIn = computed(() => Boolean(token.value && user.value))
  const displayName = computed(() => user.value?.displayName ?? '')

  async function loginWithPassword(email: string, password: string): Promise<void> {
    isLoading.value = true
    try {
      const result = await login({ email, password })
      token.value = result.accessToken
      user.value = result.user
      localStorage.setItem(AUTH_TOKEN_KEY, result.accessToken)
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
    if (!token.value) {
      return
    }
    try {
      user.value = await getMe(token.value)
    }
    catch {
      logout()
    }
  }

  function logout(): void {
    token.value = null
    user.value = null
    localStorage.removeItem(AUTH_TOKEN_KEY)
  }

  return {
    displayName,
    hydrateFromStorage,
    isLoading,
    isLoggedIn,
    loginWithPassword,
    logout,
    registerWithPassword,
    token,
    user,
  }
})
