import type { ReactionType } from '@/api/likes'
import type { SubmitReviewInput } from '@/api/reviews'
import type { CourseComment } from '@/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { reactToReview } from '@/api/likes'
import { createReview, deleteReview, getMyReviews, getReviews } from '@/api/reviews'
import { useAuthStore } from '@/stores/useAuthStore'

export const useReviewStore = defineStore('review', () => {
  const reviewsByCourse = ref<Record<number, CourseComment[]>>({})
  const myReviews = ref<CourseComment[]>([])
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
    if (!authStore.isLoggedIn)
      throw new Error('登入後才能提交評價')

    const created = await createReview(courseId, payload)
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

  async function reactToItem(courseId: number, reviewId: number, reaction: ReactionType): Promise<void> {
    const current = reviewsByCourse.value[courseId] ?? []
    reviewsByCourse.value = {
      ...reviewsByCourse.value,
      [courseId]: current.map(r =>
        r.id !== reviewId
          ? r
          : {
              ...r,
              likes: reaction === 'like' ? r.likes + 1 : r.likes,
              dislikes: reaction === 'dislike' ? r.dislikes + 1 : r.dislikes,
            },
      ),
    }
    await reactToReview(courseId, reviewId, reaction)
  }

  async function fetchMyReviews(): Promise<void> {
    const authStore = useAuthStore()
    if (!authStore.isLoggedIn)
      throw new Error('請先登入')

    isLoading.value = true
    try {
      myReviews.value = await getMyReviews()
    }
    finally {
      isLoading.value = false
    }
  }

  async function removeReview(courseId: number, reviewId: number): Promise<void> {
    const authStore = useAuthStore()
    if (!authStore.isLoggedIn)
      throw new Error('登入後才能刪除評價')

    await deleteReview(courseId, reviewId)

    const current = reviewsByCourse.value[courseId] ?? []
    reviewsByCourse.value = {
      ...reviewsByCourse.value,
      [courseId]: current.filter(review => review.id !== reviewId),
    }
    myReviews.value = myReviews.value.filter(review => review.id !== reviewId)
  }

  return {
    fetchReviews,
    fetchMyReviews,
    getCourseReviews,
    isLoading,
    myReviews,
    reactToItem,
    removeReview,
    reviewsByCourse,
    submitReview,
    totalReviewCount,
  }
})
