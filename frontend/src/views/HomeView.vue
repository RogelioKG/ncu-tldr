<script setup lang="ts">
import type { Course, SortCriterion, WishCourse } from '@/types'
import { useDebounceFn } from '@vueuse/core'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import CourseFilterSort from '@/components/CourseFilterSort.vue'
import CourseGrid from '@/components/CourseGrid.vue'
import CoursePagination from '@/components/CoursePagination.vue'
import SavedCoursesPanel from '@/components/SavedCoursesPanel.vue'
import SearchBar from '@/components/SearchBar.vue'
import WishingWell from '@/components/WishingWell.vue'
import { useSavedCourses } from '@/composables/useSavedCourses'
import { useCourseStore } from '@/stores/useCourseStore'

const router = useRouter()
const { savedCourses: orderedSavedCourses, savedCourseIds } = useSavedCourses()
const courseStore = useCourseStore()

const sortCriteria = computed<SortCriterion[]>({
  get: () => courseStore.sortCriteria,
  set: value => courseStore.setSortCriteria(value),
})

// --- 分頁 ---
const pageSize = ref(20)
const currentPage = ref(1)

const sortedCourses = computed(() => {
  const ids = savedCourseIds.value
  const saved = orderedSavedCourses.value.filter(c =>
    courseStore.filteredCourses.some(row => row.id === c.id),
  )
  const unsaved = [...courseStore.filteredCourses].filter(c => !ids.has(c.id))

  return [...saved, ...unsaved]
})

// 總頁數
const totalPages = computed(() =>
  Math.max(1, Math.ceil(sortedCourses.value.length / pageSize.value)),
)

// 當前頁面的課程
const pagedCourses = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return sortedCourses.value.slice(start, start + pageSize.value)
})

// 排序或每頁數量改變時重置回第一頁
watch([sortCriteria, pageSize], () => {
  currentPage.value = 1
}, { deep: true })

watch(() => courseStore.searchQuery, () => {
  currentPage.value = 1
})

onMounted(async () => {
  await courseStore.fetchCourses()
})

function handleSelectCourse(course: Course) {
  router.push({ name: 'course-detail', params: { id: course.id } })
}

const handleSearch = useDebounceFn((query: string) => {
  courseStore.setSearchQuery(query)
}, 300)

function handleWishCourseSelect(course: WishCourse) {
  router.push({ name: 'course-detail', params: { id: course.id } })
}
</script>

<template>
  <div class="main__container">
    <!-- 左側：許願池 -->
    <WishingWell @select-course="handleWishCourseSelect" />

    <!-- 右側：主要內容 -->
    <div class="main__content">
      <!-- 搜尋欄 -->
      <div class="main__search">
        <SearchBar @search="handleSearch" />
      </div>

      <!-- 篩選與排序控制 -->
      <CourseFilterSort
        :sort-criteria="sortCriteria"
        :page-size="pageSize"
        @update:sort-criteria="sortCriteria = $event"
        @update:page-size="pageSize = $event"
      >
        <SavedCoursesPanel />
      </CourseFilterSort>

      <!-- 課程網格 -->
      <section class="main__grid-section">
        <CourseGrid
          :courses="pagedCourses"
          @select-course="handleSelectCourse"
        />
      </section>

      <!-- 分頁導覽 -->
      <CoursePagination
        :current-page="currentPage"
        :total-pages="totalPages"
        @update:current-page="currentPage = $event"
      />
    </div>
  </div>
</template>

<style scoped>
.main__container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--spacing-xl);
  display: flex;
  gap: var(--spacing-2xl);
  align-items: flex-start;
}

.main__content {
  flex: 1;
  min-width: 0;
}

.main__search {
  display: flex;
  justify-content: center;
  margin-bottom: var(--spacing-2xl);
}

.main__grid-section {
  margin-bottom: var(--spacing-2xl);
}

/* 響應式設計 */
@media (max-width: 1024px) {
  .main__container {
    flex-direction: column;
    padding: 0 var(--spacing-md);
  }

  .main__content {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .main__search {
    padding: 0 var(--spacing-md);
  }
}
</style>
