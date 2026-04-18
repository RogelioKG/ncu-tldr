<script setup lang="ts">
import type { Course, CourseComment, TimeSlot } from '@/types'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import CourseAISummary from '@/components/CourseAISummary.vue'
import CourseBasicInfo from '@/components/CourseBasicInfo.vue'
import CourseComments from '@/components/CourseComments.vue'
import CourseStarEvaluation from '@/components/CourseStarEvaluation.vue'
import SearchBar from '@/components/SearchBar.vue'
import TimeSlotButton from '@/components/TimeSlotButton.vue'
import TimeSlotPanel from '@/components/TimeSlotPanel.vue'
import { useSavedCourses } from '@/composables/useSavedCourses'
import { useCourseStore } from '@/stores/useCourseStore'

const props = defineProps<{
  course: Course
  reviews?: CourseComment[]
  comments?: CourseComment[]
}>()
const emit = defineEmits<{
  reply: [{ parentId: number, content: string }]
  submitReview: [
    payload: {
      title: string
      content: string
      ratings: {
        gain: number
        highScore: number
        easiness: number
        teacherStyle: number
      }
      weeklyHours: string
      textbook: string
      semester: string
    },
  ]
}>()

const router = useRouter()
const courseStore = useCourseStore()
const { isSaved, toggleSave } = useSavedCourses()

const saved = computed(() => isSaved(props.course.id))
const showSlotPanel = ref(false)
const hasActiveSlots = computed(() => courseStore.selectedSlots.length > 0)

function handleToggleSave() {
  toggleSave(props.course.id)
}

function handleSearch(query: string): void {
  courseStore.setSearchQuery(query)
  router.push({ name: 'home' })
}

function handleSlotSubmit(slots: TimeSlot[]): void {
  courseStore.setSelectedSlots(slots)
  router.push({ name: 'home' })
}

function handleReply(payload: { parentId: number, content: string }) {
  emit('reply', payload)
}

function handleSubmitReview(payload: {
  title: string
  content: string
  ratings: {
    gain: number
    highScore: number
    easiness: number
    teacherStyle: number
  }
  weeklyHours: string
  textbook: string
  semester: string
}) {
  emit('submitReview', payload)
}
</script>

<template>
  <div class="course-detail-page">
    <main class="cdp__main">
      <!-- 頂部列：課程標題 + 儲存按鈕 + 搜尋框 -->
      <div class="cdp__top-row">
        <div class="cdp__title-group">
          <h1 class="cdp__course-name">
            {{ course.name }}
          </h1>
          <button
            type="button"
            class="cdp__save-btn"
            :class="{ 'cdp__save-btn--active': saved }"
            :title="saved ? '從清單移除' : '儲存至清單'"
            @click="handleToggleSave"
          >
            <span class="cdp__save-icon">{{ saved ? '⚑' : '⚐' }}</span>
            <span class="cdp__save-label">
              {{ saved ? '已儲存' : '儲存至清單' }}
            </span>
          </button>
        </div>
        <div class="cdp__search-wrapper">
          <SearchBar @search="handleSearch" />
          <TimeSlotButton :has-active="hasActiveSlots" @open="showSlotPanel = true" />
        </div>
        <TimeSlotPanel
          :visible="showSlotPanel"
          :active-slots="courseStore.selectedSlots"
          @close="showSlotPanel = false"
          @submit="handleSlotSubmit"
        />
      </div>

      <!-- AI Hashtags -->
      <div class="cdp__tags">
        <span
          v-for="tag in course.tags.slice(0, 6)"
          :key="tag"
          class="cdp__tag"
        >
          #{{ tag }}
        </span>
      </div>

      <!-- 左右兩欄 Layout -->
      <div class="cdp__layout">
        <!-- 左側欄：課程基本資訊 + 星星評價 -->
        <aside class="cdp__sidebar">
          <CourseBasicInfo :course="course" />
          <CourseStarEvaluation v-if="course.ratings" :ratings="course.ratings" />
        </aside>

        <!-- 右側欄：AI 摘要 + 留言 -->
        <div class="cdp__content">
          <CourseAISummary
            :summary="course.summary"
            :course-name="course.name"
            @submit-review="handleSubmitReview"
          />
          <CourseComments
            :comments="comments ?? []"
            @reply="handleReply"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.cdp__main {
  min-height: 100vh;
  padding: 24px var(--spacing-xl) var(--spacing-2xl);
  max-width: 1300px;
  margin: 0 auto;
}

/* 頂部列 */
.cdp__top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-md);
}

.cdp__title-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  min-width: 0;
}

.cdp__course-name {
  font-size: var(--font-size-3xl);
  font-weight: 900;
  color: var(--color-text-primary);
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.cdp__save-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border: 1px solid var(--color-tag-bg);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.cdp__save-btn:hover {
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
}

.cdp__save-btn--active {
  background: rgba(127, 169, 184, 0.12);
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
}

.cdp__save-icon {
  font-size: 16px;
  line-height: 1;
}

.cdp__search-wrapper {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

/* Hashtags */
.cdp__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-xl);
}

.cdp__tag {
  padding: 6px 18px;
  border-radius: var(--radius-full);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(0, 0, 0, 0.04);
  transition: all var(--transition-fast);
}

.cdp__tag:hover {
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
}

/* 左右兩欄 */
.cdp__layout {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: var(--spacing-xl);
  align-items: start;
}

.cdp__sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
  position: sticky;
  top: 100px;
}

.cdp__content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

/* 響應式 */
@media (max-width: 1024px) {
  .cdp__layout {
    grid-template-columns: 300px 1fr;
  }
}

@media (max-width: 860px) {
  .cdp__layout {
    grid-template-columns: 1fr;
  }

  .cdp__sidebar {
    position: static;
    flex-direction: row;
    flex-wrap: wrap;
  }

  .cdp__sidebar > * {
    flex: 1;
    min-width: 280px;
  }
}

@media (max-width: 680px) {
  .cdp__main {
    padding: 88px var(--spacing-md) var(--spacing-xl);
  }

  .cdp__top-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .cdp__search-wrapper {
    width: 100%;
  }

  .cdp__course-name {
    font-size: var(--font-size-2xl);
  }

  .cdp__sidebar {
    flex-direction: column;
  }

  .cdp__sidebar > * {
    min-width: unset;
  }
}
</style>
