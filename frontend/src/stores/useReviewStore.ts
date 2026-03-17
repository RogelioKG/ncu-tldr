import type { CourseComment } from '@/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { createReview, getReviews } from '@/api/reviews'

const DATE_DASH_REGEX = /-/g

export const useReviewStore = defineStore('review', () => {
  const reviewsByCourse = ref<Record<number, CourseComment[]>>({})
  const isLoading = ref(false)

  const totalReviewCount = computed(() =>
    Object.values(reviewsByCourse.value).reduce((sum, rows) => sum + rows.length, 0),
  )

  async function fetchReviews(courseId: number): Promise<void> {
    isLoading.value = true
    try {
      const rows = await getReviews(courseId)
      reviewsByCourse.value = {
        ...reviewsByCourse.value,
        [courseId]: rows,
      }
    }
    finally {
      isLoading.value = false
    }
  }

  async function submitReview(
    courseId: number,
    payload: {
      user: string
      title: string
      content: string
      ratings: {
        reward: number
        score: number
        easiness: number
        teacherStyle: number
      }
    },
  ): Promise<CourseComment> {
    const created = await createReview(courseId, payload)
    const enriched: CourseComment = {
      ...created,
      ratings: payload.ratings,
    }
    const current = reviewsByCourse.value[courseId] ?? []
    reviewsByCourse.value = {
      ...reviewsByCourse.value,
      [courseId]: [...current, enriched],
    }
    return enriched
  }

  function getCourseReviews(courseId: number): CourseComment[] {
    return reviewsByCourse.value[courseId] ?? []
  }

  function addReply(
    courseId: number,
    parentId: number,
    content: string,
    user?: string,
  ): CourseComment {
    const current = reviewsByCourse.value[courseId] ?? []
    const nextId = current.reduce((max, c) => Math.max(max, c.id), 0) + 1
    const created: CourseComment = {
      id: nextId,
      user: user ?? '匿名同學',
      title: content.slice(0, 50),
      content,
      date: new Date().toISOString().slice(0, 10).replace(DATE_DASH_REGEX, '/'),
      likes: 0,
      dislikes: 0,
      parentId,
    }
    reviewsByCourse.value = {
      ...reviewsByCourse.value,
      [courseId]: [...current, created],
    }
    return created
  }

  return {
    addReply,
    fetchReviews,
    getCourseReviews,
    isLoading,
    reviewsByCourse,
    submitReview,
    totalReviewCount,
  }
})
