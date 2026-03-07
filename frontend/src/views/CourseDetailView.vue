<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import CourseDetail from '@/components/CourseDetail.vue'
import { useAuthStore } from '@/stores/useAuthStore'
import { useCourseStore } from '@/stores/useCourseStore'
import { useReviewStore } from '@/stores/useReviewStore'

const route = useRoute()
const authStore = useAuthStore()
const courseStore = useCourseStore()
const reviewStore = useReviewStore()

const courseId = computed(() => {
  const id = route.params.id
  return typeof id === 'string' ? Number.parseInt(id, 10) : Number(id)
})

const course = computed(() => {
  const selected = courseStore.selectedCourse
  if (selected && selected.id === courseId.value) {
    const reviews = reviewStore.getCourseReviews(selected.id)
    return {
      ...selected,
      comments: reviews.length > 0 ? reviews : selected.comments,
    }
  }
  return null
})

async function loadData() {
  if (Number.isNaN(courseId.value)) {
    return
  }
  await Promise.all([
    courseStore.fetchCourseById(courseId.value),
    reviewStore.fetchReviews(courseId.value),
  ])
}

async function handleSubmitReview(payload: {
  title: string
  content: string
  ratings: {
    reward: number
    score: number
    easiness: number
    teacherStyle: number
  }
}) {
  if (!courseStore.selectedCourse) {
    return
  }
  const selected = courseStore.selectedCourse
  const reviewCount = selected.summary?.reviewCount ?? 0
  const nextCount = reviewCount + 1
  const nextRatings = {
    reward: Number((((selected.ratings.reward * reviewCount) + payload.ratings.reward) / nextCount).toFixed(2)),
    score: Number((((selected.ratings.score * reviewCount) + payload.ratings.score) / nextCount).toFixed(2)),
    easiness: Number((((selected.ratings.easiness * reviewCount) + payload.ratings.easiness) / nextCount).toFixed(2)),
    teacherStyle: Number((((selected.ratings.teacherStyle * reviewCount) + payload.ratings.teacherStyle) / nextCount).toFixed(2)),
  }
  await reviewStore.submitReview(courseId.value, {
    user: authStore.displayName || '匿名同學',
    title: payload.title,
    content: payload.content,
    ratings: payload.ratings,
  })
  courseStore.applyReviewRatings(courseId.value, nextRatings)
}

watch(courseId, async () => {
  await loadData()
})

onMounted(async () => {
  await loadData()
})
</script>

<template>
  <div class="course-detail-view">
    <div v-if="course">
      <CourseDetail :course="course" @submit-review="handleSubmitReview" />
    </div>
    <div v-else class="not-found">
      <p>找不到該課程資訊。</p>
    </div>
  </div>
</template>

<style scoped>
.course-detail-view {
  width: 100%;
}

.not-found {
  text-align: center;
  padding: 4rem;
  color: var(--color-text-muted);
  font-size: 1.2rem;
}
</style>
