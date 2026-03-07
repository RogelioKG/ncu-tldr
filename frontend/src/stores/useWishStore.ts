import type { WishCourse } from '@/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { addWish, getWishlist, removeWish } from '@/api/wishlist'

export const useWishStore = defineStore('wish', () => {
  const wishes = ref<WishCourse[]>([])
  const isLoading = ref(false)

  const sortedWishes = computed(() =>
    [...wishes.value].sort((a, b) => (b.voteCount ?? 0) - (a.voteCount ?? 0)),
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

  async function createWish(payload: { name: string, teacher: string }): Promise<void> {
    const saved = await addWish(payload)
    const target = wishes.value.find(row => row.id === saved.id)
    if (!target) {
      wishes.value = [...wishes.value, saved]
      return
    }
    target.voteCount = saved.voteCount
  }

  async function deleteWish(wishId: number): Promise<void> {
    await removeWish(wishId)
    wishes.value = wishes.value.filter(row => row.id !== wishId)
  }

  return {
    createWish,
    deleteWish,
    fetchWishlist,
    isLoading,
    sortedWishes,
    wishes,
  }
})
