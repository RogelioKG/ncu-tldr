<script setup lang="ts">
import type { Course } from '@/types'
// CourseCard 元件 - 課程卡片（內容同 CourseDetail）
import { computed, ref } from 'vue'
import { useSavedCourses } from '@/composables/useSavedCourses'
import StarRating from './StarRating.vue'

const props = defineProps<Props>()

const emit = defineEmits<{
  select: [course: Course]
}>()

interface Props {
  course: Course
}

const isHovered = ref(false)

const { isSaved, toggleSave } = useSavedCourses()
const saved = computed(() => isSaved(props.course.id))

function handleToggleSave(e: Event) {
  e.stopPropagation()
  toggleSave(props.course.id)
}

function handleClick() {
  emit('select', props.course)
}
</script>

<template>
  <div
    class="course-card"
    :class="{ 'course-card--hovered': isHovered }"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
    @click="handleClick"
  >
    <div class="course-card__body">
      <div class="course-card__rating-row">
        <button
          type="button"
          class="course-card__save-btn"
          :class="{ 'course-card__save-btn--active': saved }"
          :title="saved ? '從清單移除' : '儲存至清單'"
          @click="handleToggleSave"
        >
          {{ saved ? '⚑' : '⚐' }}
        </button>
      </div>
      <header class="course-card__header">
        <h2 class="course-card__title">
          {{ course.name }}
        </h2>
        <div class="course-card__divider" />
        <p class="course-card__teacher">
          教師：{{ props.course.teacher }}
        </p>
      </header>

      <div class="course-card__tags">
        <span
          v-for="tag in props.course.tags"
          :key="tag"
          class="course-card__tag"
        >
          #{{ tag }}
        </span>
      </div>

      <div v-if="props.course.ratings" class="course-card__ratings">
        <StarRating
          :rating="props.course.ratings.reward"
          label="收穫"
          size="sm"
        />
        <StarRating
          :rating="props.course.ratings.score"
          label="分數"
          size="sm"
        />
        <StarRating
          :rating="props.course.ratings.easiness"
          label="輕鬆"
          size="sm"
        />
        <StarRating
          :rating="props.course.ratings.teacherStyle"
          label="教師風格"
          size="sm"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 設計原則：子元素不可超出父元素。卡片與內容區使用 overflow 控制，評分區空間不足時可捲動。 */
.course-card {
  position: relative;
  height: 100%;
  min-width: var(--course-card-min-width); /* 保護四行星星區塊不被壓縮 */
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  flex-direction: column;
  min-height: 140px;
  overflow: hidden; /* 子元素不可超出卡片範圍 */
}

.course-card:hover,
.course-card--hovered {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-accent-primary);
}

/* 內容區：可縮小，子元素不超出 */
.course-card__body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.course-card__rating-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
}

.course-card__save-btn {
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: var(--color-text-muted);
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.course-card__save-btn:hover {
  color: var(--color-accent-primary);
  background: rgba(127, 169, 184, 0.1);
}

.course-card__save-btn--active {
  color: var(--color-accent-primary);
}

.course-card__header {
  text-align: center;
  margin-bottom: var(--spacing-sm);
}

.course-card__title {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
  letter-spacing: 0.5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-card__divider {
  width: 60%;
  max-width: 120px;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--color-accent-primary),
    transparent
  );
  margin: 0 auto var(--spacing-sm);
  border-radius: var(--radius-full);
}

.course-card__teacher {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.course-card__tags {
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  justify-content: center;
  gap: var(--spacing-xs);
  min-height: var(--row-tags-height, 0px);
  margin-bottom: var(--spacing-sm);
}

.course-card__tag {
  font-size: 0.65rem;
  color: var(--color-tag-text);
  background: var(--color-tag-bg);
  padding: 2px var(--spacing-xs);
  border-radius: var(--radius-full);
}

.course-card__ratings {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center; /* 四組「文字+星星」整組置中 */
  gap: var(--spacing-xs);
  padding: var(--spacing-sm);
  background: var(--color-background);
  border-radius: var(--radius-md);
  margin-top: auto;
}
</style>
