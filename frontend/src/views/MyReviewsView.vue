<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
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

    <ul v-else class="my-reviews__list">
      <li v-for="review in reviewStore.myReviews" :key="review.id" class="my-reviews__item">
        <div class="my-reviews__item-top">
          <p class="my-reviews__item-title">
            {{ review.title }}
          </p>
          <span class="my-reviews__item-date">{{ review.date }}</span>
        </div>
        <p class="my-reviews__item-content">
          {{ review.content }}
        </p>
        <div class="my-reviews__actions">
          <button
            v-if="review.canDelete"
            type="button"
            class="my-reviews__delete-btn"
            @click="handleDeleteReview(review.courseId, review.id)"
          >
            刪除評價
          </button>
        </div>
      </li>
    </ul>
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

.my-reviews__item {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.my-reviews__item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.my-reviews__item-title {
  font-weight: 700;
  color: var(--color-text-primary);
}

.my-reviews__item-date {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.my-reviews__item-content {
  margin-top: var(--spacing-sm);
  color: var(--color-text-secondary);
}

.my-reviews__actions {
  margin-top: var(--spacing-md);
  display: flex;
  justify-content: flex-end;
}

.my-reviews__delete-btn {
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  background: var(--color-background-alt);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  transition: var(--transition-fast);
}

.my-reviews__delete-btn:hover {
  background: #ffe8e8;
  color: #b02222;
}
</style>
