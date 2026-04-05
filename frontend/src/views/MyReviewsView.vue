<script setup lang="ts">
import { computed } from 'vue'
import { useDiscussionStore } from '@/stores/useDiscussionStore'

const discussionStore = useDiscussionStore()
const groupedReviews = computed(() => Object.entries(discussionStore.discussionsByCourse))
</script>

<template>
  <section class="my-reviews">
    <h1 class="my-reviews__title">
      我的評價
    </h1>
    <p class="my-reviews__subtitle">
      目前共 {{ discussionStore.totalDiscussionCount }} 筆
    </p>
    <div v-if="groupedReviews.length === 0" class="my-reviews__empty">
      目前還沒有提交任何評價
    </div>
    <div v-else class="my-reviews__groups">
      <article
        v-for="[courseId, reviews] in groupedReviews"
        :key="courseId"
        class="my-reviews__group"
      >
        <h2 class="my-reviews__group-title">
          課程 #{{ courseId }}
        </h2>
        <ul class="my-reviews__list">
          <li
            v-for="review in reviews"
            :key="review.id"
            class="my-reviews__item"
          >
            <strong>{{ review.title }}</strong>
            <p>{{ review.content }}</p>
          </li>
        </ul>
      </article>
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
  margin-bottom: var(--spacing-sm);
}

.my-reviews__subtitle {
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-lg);
}

.my-reviews__empty {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
}

.my-reviews__groups {
  display: grid;
  gap: var(--spacing-lg);
}

.my-reviews__group {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
}

.my-reviews__group-title {
  margin-bottom: var(--spacing-sm);
}

.my-reviews__list {
  display: grid;
  gap: var(--spacing-sm);
}

.my-reviews__item {
  border: 1px solid var(--color-background-alt);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
}
</style>
