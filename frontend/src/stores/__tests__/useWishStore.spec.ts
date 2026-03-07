import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useWishStore } from '../useWishStore'

vi.mock('@/api/wishlist', () => ({
  getWishlist: vi.fn(),
  addWish: vi.fn(),
  removeWish: vi.fn(),
}))

describe('useWishStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('fetches and sorts wishes by vote count', async () => {
    const { getWishlist } = await import('@/api/wishlist')
    vi.mocked(getWishlist).mockResolvedValueOnce([
      { id: 1, name: 'A', teacher: 'T1', voteCount: 1 },
      { id: 2, name: 'B', teacher: 'T2', voteCount: 4 },
    ])

    const store = useWishStore()
    await store.fetchWishlist()
    expect(store.sortedWishes[0]?.id).toBe(2)
  })

  it('creates wish and updates vote count', async () => {
    const { addWish } = await import('@/api/wishlist')
    vi.mocked(addWish).mockResolvedValueOnce({
      id: 3,
      name: '新課程',
      teacher: '老師',
      voteCount: 1,
    })

    const store = useWishStore()
    await store.createWish({ name: '新課程', teacher: '老師' })
    expect(store.wishes).toHaveLength(1)
    expect(store.wishes[0]?.voteCount).toBe(1)
  })
})
