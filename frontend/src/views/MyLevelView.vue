<script setup lang="ts">
import { computed } from 'vue'
import { useReviewStore } from '@/stores/useReviewStore'

const reviewStore = useReviewStore()
const level = computed(() => {
  const count = reviewStore.totalReviewCount
  if (count >= 20) {
    return 'TLDR Master'
  }
  if (count >= 10) {
    return 'Course Guide'
  }
  if (count >= 3) {
    return 'Active Reviewer'
  }
  return 'New Explorer'
})
</script>

<template>
  <section class="my-level">
    <h1 class="my-level__title">
      我的等級
    </h1>
    <div class="my-level__card">
      <p class="my-level__label">
        目前等級
      </p>
      <p class="my-level__value">
        {{ level }}
      </p>
      <p class="my-level__progress">
        已提交 {{ reviewStore.totalReviewCount }} 筆評價
      </p>
    </div>
  </section>
</template>

<style scoped>
.my-level {
  max-width: 720px;
  margin: 0 auto;
  padding: var(--spacing-xl);
}

.my-level__title {
  margin-bottom: var(--spacing-lg);
}

.my-level__card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-xl);
}

.my-level__label {
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-xs);
}

.my-level__value {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-accent-primary);
}

.my-level__progress {
  margin-top: var(--spacing-md);
}
</style>
