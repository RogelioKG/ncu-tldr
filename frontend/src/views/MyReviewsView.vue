<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ReviewCard from '@/components/ReviewCard.vue'
import { useAuthStore } from '@/stores/useAuthStore'
import { useReviewStore } from '@/stores/useReviewStore'

const router = useRouter()
const authStore = useAuthStore()
const reviewStore = useReviewStore()

onMounted(async () => {
  if (!authStore.isLoggedIn) {
    router.push({ name: 'login' })
    return
  }
  await reviewStore.fetchMyReviews()
})

async function handleDeleteReview(courseId: number | undefined, reviewId: number) {
  if (courseId == null)
    return
  await reviewStore.removeReview(courseId, reviewId)
}
</script>

<template>
  <section class="my-reviews">
    <h1 class="my-reviews__title">
      我的評價
    </h1>

    <div v-if="reviewStore.isLoading" class="my-reviews__pending">
      <p class="my-reviews__pending-text">
        載入中...
      </p>
    </div>

    <div v-else-if="reviewStore.myReviews.length === 0" class="my-reviews__pending">
      <p class="my-reviews__pending-text">
        目前沒有可顯示的評價。
      </p>
    </div>

    <div v-else class="my-reviews__list">
      <ReviewCard
        v-for="review in reviewStore.myReviews"
        :key="review.id"
        :review="review"
        :show-delete="review.canDelete"
        @delete="handleDeleteReview(review.courseId, $event.reviewId)"
      />
    </div>
  </section>
</template>

<style scoped>
.my-reviews {
  max-width: 960px;
  margin: 0 auto;
  padding: var(--spacing-xl);
}

.my-reviews__title {
  margin-bottom: var(--spacing-lg);
}

.my-reviews__pending {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  color: var(--color-text-muted);
}

.my-reviews__list {
  display: grid;
  gap: var(--spacing-md);
}
</style>
