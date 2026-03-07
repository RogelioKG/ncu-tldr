import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useReviewStore } from '../useReviewStore'

vi.mock('@/api/reviews', () => ({
  getReviews: vi.fn(),
  createReview: vi.fn(),
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

  it('submits review with ratings metadata', async () => {
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
      user: 'User',
      title: '心得',
      content: '內容',
      ratings: {
        reward: 5,
        score: 4,
        easiness: 3,
        teacherStyle: 4,
      },
    })
    expect(saved.ratings?.reward).toBe(5)
    expect(store.getCourseReviews(1)).toHaveLength(1)
  })
})
