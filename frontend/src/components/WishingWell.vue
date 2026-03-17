<script setup lang="ts">
import type { WishCourse } from '@/types'
// WishingWell 元件 - 許願池側邊欄
import { onMounted, ref } from 'vue'
import wishingWellImg from '@/assets/wishing_well_spritual_no_bg.png'
import { useWishStore } from '@/stores/useWishStore'
import WishingWellFormToast from './WishingWellFormToast.vue'

const emit = defineEmits<{
  selectCourse: [course: WishCourse]
}>()

const wishStore = useWishStore()
const hoveredItem = ref<number | null>(null)
const showWishForm = ref(false)

function handleSelectCourse(course: WishCourse) {
  emit('selectCourse', course)
}

function handleSubmitWish(_payload: { name: string, teacher: string }) {
  /* Form handles createWish and shows success/failure; emit kept for optional parent side effects */
}

onMounted(async () => {
  await wishStore.fetchWishlist()
})
</script>

<template>
  <aside class="wishing-well">
    <!-- 裝飾性背景卡片 -->
    <div class="wishing-well__bg-card wishing-well__bg-card--1" />
    <div class="wishing-well__bg-card wishing-well__bg-card--2" />

    <!-- 主卡片 -->
    <div class="wishing-well__card">
      <header class="wishing-well__header">
        <span class="wishing-well__icon">✨</span>
        <h2 class="wishing-well__title">
          許願池
        </h2>
      </header>

      <div class="wishing-well__body">
        <ul class="wishing-well__list">
          <li
            v-for="(course, index) in wishStore.sortedWishes"
            :key="course.id"
            class="wishing-well__item"
            :class="{ 'wishing-well__item--hovered': hoveredItem === course.id }"
            @mouseenter="hoveredItem = course.id"
            @mouseleave="hoveredItem = null"
            @click="handleSelectCourse(course)"
          >
            <span class="wishing-well__number">{{ index + 1 }}.</span>
            <div class="wishing-well__course-info">
              <span class="wishing-well__course-name">{{ course.name }}</span>
              <span class="wishing-well__separator">-</span>
              <span class="wishing-well__teacher">{{ course.teacher }}</span>
              <span v-if="course.voteCount" class="wishing-well__votes">({{ course.voteCount }} 人)</span>
            </div>
          </li>
        </ul>

        <button
          type="button"
          class="wishing-well__add-btn"
          aria-label="許願池"
          @click="showWishForm = true"
        >
          <span class="wishing-well__add-wrap">
            <img
              :src="wishingWellImg"
              alt="許願池"
              class="wishing-well__add-img"
            >
            <span class="wishing-well__add-hint">點此向課程女神許願</span>
          </span>
        </button>
      </div>
    </div>

    <WishingWellFormToast
      v-if="showWishForm"
      @close="showWishForm = false"
      @submit="handleSubmitWish"
    />
  </aside>
</template>

<style scoped>
.wishing-well {
  position: relative;
  width: 280px;
  flex-shrink: 0;
}

/* 裝飾性背景卡片 - 堆疊效果 */
.wishing-well__bg-card {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background: linear-gradient(135deg, var(--color-accent-teal) 0%, var(--color-accent-secondary) 100%);
  border-radius: var(--radius-lg);
  opacity: 0.6;
}

.wishing-well__bg-card--1 {
  transform: rotate(-3deg) translateX(-8px);
}

.wishing-well__bg-card--2 {
  transform: rotate(-1.5deg) translateX(-4px);
  opacity: 0.8;
}

/* 主卡片 */
.wishing-well__card {
  position: relative;
  background: var(--wishing-well-gradient);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.wishing-well__header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid rgba(127, 169, 184, 0.2);
}

.wishing-well__icon {
  font-size: var(--font-size-lg);
}

.wishing-well__title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: 1px;
}

.wishing-well__body {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.wishing-well__list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin-bottom: 0;
}

.wishing-well__item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-left: calc(var(--spacing-sm) * -1);
  margin-right: calc(var(--spacing-sm) * -1);
}

.wishing-well__item:hover,
.wishing-well__item--hovered {
  background: rgba(255, 255, 255, 0.6);
}

.wishing-well__number {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-accent-primary);
  min-width: 20px;
}

.wishing-well__course-info {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--spacing-xs);
  line-height: 1.4;
}

.wishing-well__course-name {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.wishing-well__separator {
  color: var(--color-text-muted);
}

.wishing-well__teacher {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: 400;
}

.wishing-well__votes {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.wishing-well__add-btn {
  display: block;
  width: 100%;
  padding: 0;
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.wishing-well__add-btn:hover {
  opacity: 0.9;
}

.wishing-well__add-wrap {
  position: relative;
  display: block;
  width: 100%;
}

.wishing-well__add-img {
  display: block;
  width: 100%;
  height: auto;
  object-fit: contain;
  border-radius: var(--radius-md);
}

.wishing-well__add-hint {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-sm);
  font-weight: 600;
  letter-spacing: 1px;
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 2px 6px rgba(20, 48, 60, 0.28);
  transform-origin: center;
  animation: wishing-well-hint-pulse 2.2s ease-in-out infinite;
  pointer-events: none;
}

.wishing-well__add-btn:hover .wishing-well__add-hint {
  animation-duration: 1.7s;
}

@keyframes wishing-well-hint-pulse {
  0%,
  100% {
    transform: translateY(0) scale(1);
    opacity: 0.58;
  }
  35% {
    transform: translateY(-4px) scale(1.08);
    opacity: 0.8;
  }
  65% {
    transform: translateY(1px) scale(0.95);
    opacity: 0.68;
  }
}

@media (max-width: 1024px) {
  .wishing-well {
    width: 100%;
  }

  .wishing-well__body {
    display: flex;
    flex-direction: row;
    align-items: stretch;
    gap: var(--spacing-md);
  }

  .wishing-well__list {
    flex: 1 1 auto;
    min-width: 0;
  }

  .wishing-well__add-btn {
    flex: 0 0 auto;
    width: auto;
    height: auto;
    min-width: 110px;
    max-width: 220px;
    display: flex;
    align-self: stretch;
    align-items: stretch;
  }

  .wishing-well__add-wrap {
    display: flex;
    width: 100%;
    min-height: 0;
  }

  .wishing-well__add-img {
    width: auto;
    height: 100%;
    object-fit: contain;
  }
}

@media (max-width: 640px) {
  .wishing-well__add-btn {
    min-width: 88px;
    max-width: 140px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .wishing-well__add-hint {
    animation: none;
    opacity: 0.72;
  }
}
</style>
