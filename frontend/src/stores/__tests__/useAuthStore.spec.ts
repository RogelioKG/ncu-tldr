import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useAuthStore } from '../useAuthStore'

vi.mock('@/api/auth', () => ({
  login: vi.fn(),
  register: vi.fn(),
  getMe: vi.fn(),
  logoutApi: vi.fn(),
}))

describe('useAuthStore', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('logs in and sets user', async () => {
    const { login } = await import('@/api/auth')
    vi.mocked(login).mockResolvedValueOnce({
      id: '1',
      email: 'demo@cc.ncu.edu.tw',
      displayName: 'Demo',
      isActive: true,
      emailVerified: true,
    })

    const store = useAuthStore()
    await store.loginWithPassword('demo@cc.ncu.edu.tw', 'password123')
    expect(store.isLoggedIn).toBe(true)
    expect(store.user?.email).toBe('demo@cc.ncu.edu.tw')
  })

  it('hydrates and logs out when getMe fails', async () => {
    const { getMe } = await import('@/api/auth')
    vi.mocked(getMe).mockRejectedValueOnce(new Error('Invalid session'))

    const store = useAuthStore()
    await store.hydrateFromStorage()
    expect(store.isLoggedIn).toBe(false)
    expect(store.user).toBeNull()
    expect(store.isInitialized).toBe(true)
  })

  it('hydration is idempotent — second call is a no-op', async () => {
    const { getMe } = await import('@/api/auth')
    vi.mocked(getMe).mockResolvedValue({
      id: '1',
      email: 'demo@cc.ncu.edu.tw',
      displayName: 'Demo',
      isActive: true,
      emailVerified: true,
    })

    const store = useAuthStore()
    await store.hydrateFromStorage()
    await store.hydrateFromStorage()
    expect(vi.mocked(getMe)).toHaveBeenCalledTimes(1)
  })
})
