import type { SubmitReviewInput } from '@/api/reviews'
import type { CourseComment } from '@/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { createReview, getReviews } from '@/api/reviews'
import { useAuthStore } from '@/stores/useAuthStore'

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
      reviewsByCourse.value = { ...reviewsByCourse.value, [courseId]: rows }
    }
    finally {
      isLoading.value = false
    }
  }

  async function submitReview(courseId: number, payload: SubmitReviewInput): Promise<CourseComment> {
    const authStore = useAuthStore()
    const token = authStore.token
    if (!token)
      throw new Error('登入後才能提交評價')

    const created = await createReview(courseId, payload, token)
    const current = reviewsByCourse.value[courseId] ?? []
    reviewsByCourse.value = {
      ...reviewsByCourse.value,
      [courseId]: [created, ...current],
    }
    return created
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
