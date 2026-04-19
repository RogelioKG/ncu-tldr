import type { WishCourse } from '@/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getWishlist, unvoteForCourse, voteForCourse } from '@/api/wishlist'

export const useWishStore = defineStore('wish', () => {
  const wishes = ref<WishCourse[]>([])
  const isLoading = ref(false)

  const sortedWishes = computed(() =>
    wishes.value.toSorted((a, b) => b.voteCount - a.voteCount),
  )

  async function fetchWishlist(): Promise<void> {
    isLoading.value = true
    try {
      wishes.value = await getWishlist()
    }
    finally {
      isLoading.value = false
    }
  }

  async function voteForCourseById(courseId: number): Promise<void> {
    await voteForCourse(courseId)
    await fetchWishlist()
  }

  async function unvoteForCourseById(courseId: number): Promise<void> {
    await unvoteForCourse(courseId)
    wishes.value = wishes.value.filter(w => w.courseId !== courseId)
  }

  return {
    fetchWishlist,
    isLoading,
    sortedWishes,
    unvoteForCourseById,
    voteForCourseById,
    wishes,
  }
})
