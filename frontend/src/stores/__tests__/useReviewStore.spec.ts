import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useReviewStore } from '../useReviewStore'

vi.mock('@/api/reviews', () => ({
  getReviews: vi.fn(),
  createReview: vi.fn(),
}))

vi.mock('@/stores/useAuthStore', () => ({
  useAuthStore: () => ({ token: 'mock-token' }),
}))

describe('useReviewStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('fetches reviews by course', async () => {
    const { getReviews } = await import('@/api/reviews')
    vi.mocked(getReviews).mockResolvedValueOnce([
      {
        id: 1,
        user: 'User',
        title: '心得',
        content: '內容',
        date: '2026-02-27',
        likes: 0,
        dislikes: 0,
      },
    ])

    const store = useReviewStore()
    await store.fetchReviews(1)
    expect(store.getCourseReviews(1)).toHaveLength(1)
    expect(store.totalReviewCount).toBe(1)
  })

  it('submits review and prepends to list', async () => {
    const { createReview } = await import('@/api/reviews')
    vi.mocked(createReview).mockResolvedValueOnce({
      id: 2,
      user: 'User',
      title: '心得',
      content: '內容',
      date: '2026-02-27',
      likes: 0,
      dislikes: 0,
    })

    const store = useReviewStore()
    const saved = await store.submitReview(1, {
      title: '心得',
      content: '內容',
      ratings: {
        gain: 5,
        highScore: 4,
        easiness: 3,
        teacherStyle: 4,
      },
    })
    expect(saved.id).toBe(2)
    expect(store.getCourseReviews(1)).toHaveLength(1)
  })
})
