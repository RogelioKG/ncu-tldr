import type { CourseComment } from '@/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { createReview, getReviews } from '@/api/reviews'

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

  return {
    fetchReviews,
    getCourseReviews,
    isLoading,
    reviewsByCourse,
    submitReview,
    totalReviewCount,
  }
})
