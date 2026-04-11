<script setup lang="ts">
// TODO: Once backend implements GET /api/v1/auth/me/reviews,
// replace this stub with: import { getMyReviews } from '@/api/reviews'
</script>

<template>
  <section class="my-reviews">
    <h1 class="my-reviews__title">
      我的評價
    </h1>
    <div class="my-reviews__pending">
      <p class="my-reviews__pending-text">
        此功能需要後端支援，即將開放。
      </p>
      <p class="my-reviews__pending-hint">
        開放後將顯示您對各課程提交的所有評價紀錄。
      </p>
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
  display: grid;
  gap: var(--spacing-sm);
}

.my-reviews__pending-hint {
  font-size: 0.875rem;
}
</style>
