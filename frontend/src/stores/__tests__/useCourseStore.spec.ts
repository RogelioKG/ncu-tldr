import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useCourseStore } from '../useCourseStore'

vi.mock('@/api/courses', () => ({
  getCourses: vi.fn(),
  getCourseById: vi.fn(),
}))

describe('useCourseStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('fetches course list', async () => {
    const { getCourses } = await import('@/api/courses')
    vi.mocked(getCourses).mockResolvedValueOnce([
      {
        id: 1,
        name: '演算法',
        teacher: '王大明',
        tags: ['實用'],
        ratings: { gain: 4.5, highScore: 4, easiness: 3, teacherStyle: 4.5 },
      },
    ])

    const store = useCourseStore()
    await store.fetchCourses()
    expect(store.courses).toHaveLength(1)
    expect(store.courses[0]?.name).toBe('演算法')
  })

  it('filters courses by search query', () => {
    const store = useCourseStore()
    store.courses = [
      {
        id: 1,
        name: '演算法',
        teacher: '王大明',
        tags: ['實用'],
        ratings: { gain: 4.5, highScore: 4, easiness: 3, teacherStyle: 4.5 },
      },
      {
        id: 2,
        name: '線性代數',
        teacher: '林博士',
        tags: ['理論'],
        ratings: { gain: 4, highScore: 3.5, easiness: 2.5, teacherStyle: 3.5 },
      },
    ]
    store.setSearchQuery('演算法')
    expect(store.filteredCourses).toHaveLength(1)
    expect(store.filteredCourses[0]?.id).toBe(1)
  })

  it('applies review ratings and increments review count', () => {
    const store = useCourseStore()
    store.courses = [{
      id: 1,
      name: '演算法',
      teacher: '王大明',
      tags: [],
      ratings: { gain: 4, highScore: 4, easiness: 4, teacherStyle: 4 },
      summary: {
        overview: 'x',
        targetAudience: 'x',
        textbook: 'x',
        prerequisites: 'x',
        weeklyHours: 'x',
        gradingItems: [],
        notes: 'x',
        reviewCount: 3,
      },
    }]
    store.applyReviewRatings(1, {
      gain: 4.5,
      highScore: 4.2,
      easiness: 3.8,
      teacherStyle: 4.6,
    })
    const updated = store.courses.find(c => c.id === 1)
    expect(updated?.ratings?.gain).toBe(4.5)
    expect(updated?.summary?.reviewCount).toBe(4)
  })
})
