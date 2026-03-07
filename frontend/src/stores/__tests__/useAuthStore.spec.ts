import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useAuthStore } from '../useAuthStore'

vi.mock('@/api/auth', () => ({
  login: vi.fn(),
  register: vi.fn(),
  getMe: vi.fn(),
}))

describe('useAuthStore', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('logs in and stores token', async () => {
    const { login } = await import('@/api/auth')
    vi.mocked(login).mockResolvedValueOnce({
      accessToken: 'mock-token',
      tokenType: 'bearer',
      user: {
        id: 1,
        email: 'demo@cc.ncu.edu.tw',
        displayName: 'Demo',
        isActive: true,
      },
    })

    const store = useAuthStore()
    await store.loginWithPassword('demo@cc.ncu.edu.tw', 'password123')
    expect(store.isLoggedIn).toBe(true)
    expect(localStorage.getItem('ncu-tldr-token')).toBe('mock-token')
  })

  it('hydrates and logs out when token invalid', async () => {
    const { getMe } = await import('@/api/auth')
    vi.mocked(getMe).mockRejectedValueOnce(new Error('Invalid token'))
    localStorage.setItem('ncu-tldr-token', 'bad-token')

    const store = useAuthStore()
    await store.hydrateFromStorage()
    expect(store.isLoggedIn).toBe(false)
    expect(store.token).toBeNull()
  })
})
