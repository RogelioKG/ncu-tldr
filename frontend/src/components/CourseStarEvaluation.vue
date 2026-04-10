<script setup lang="ts">
import type { CourseRatings } from '@/types'
import { computed } from 'vue'
import StarRating from './StarRating.vue'

const props = defineProps<{
  ratings: CourseRatings
}>()

function clampRating(value: number): number {
  return Math.max(0, Math.min(5, value))
}

const overallRating = computed(() => {
  const { gain, highScore, easiness, teacherStyle } = props.ratings
  const weighted = gain * 0.35 + highScore * 0.2 + easiness * 0.15 + teacherStyle * 0.3
  return Number(clampRating(weighted).toFixed(1))
})
</script>

<template>
  <section class="rating-card" aria-label="課程星星評價">
    <h2 class="rating-card__title">
      星星評價
    </h2>

    <div class="rating-card__headline">
      <span class="rating-card__big-star" aria-hidden="true">★</span>
      <p class="rating-card__score">
        <span class="rating-card__score-value">{{ overallRating }}</span>
        <span class="rating-card__score-max">/ 5</span>
      </p>
    </div>

    <p class="rating-card__subtitle">
      經使用者可信度加權平均
    </p>

    <div class="rating-card__metrics" aria-label="評分細項">
      <StarRating
        :rating="ratings.gain"
        label="收穫"
        size="sm"
      />
      <StarRating
        :rating="ratings.highScore"
        label="分數"
        size="sm"
      />
      <StarRating
        :rating="ratings.easiness"
        label="輕鬆"
        size="sm"
      />
      <StarRating
        :rating="ratings.teacherStyle"
        label="教師風格"
        size="sm"
      />
    </div>
  </section>
</template>

<style scoped>
.rating-card {
  padding: var(--spacing-lg);
  border-radius: var(--radius-xl);
  background:
    radial-gradient(circle at 5% 95%, rgba(203, 239, 242, 0.38), transparent 32%),
    radial-gradient(circle at 95% 8%, rgba(229, 238, 255, 0.42), transparent 30%),
    rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  box-shadow: var(--shadow-lg);
}

.rating-card__title {
  text-align: center;
  font-size: var(--font-size-xl);
  font-weight: 800;
  color: var(--color-text-primary);
  letter-spacing: 0.03em;
}

.rating-card__headline {
  margin-top: var(--spacing-md);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.rating-card__big-star {
  font-size: 48px;
  color: #f3b544;
  line-height: 1;
}

.rating-card__score {
  display: flex;
  align-items: baseline;
  gap: 6px;
  color: #111111;
}

.rating-card__score-value {
  font-size: 42px;
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1;
}

.rating-card__score-max {
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
}

.rating-card__subtitle {
  margin-top: var(--spacing-sm);
  text-align: center;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.rating-card__metrics {
  margin-top: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}
</style>
