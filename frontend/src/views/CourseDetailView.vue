<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import CourseDetail from '@/components/CourseDetail.vue'
import { useAuthStore } from '@/stores/useAuthStore'
import { useCourseStore } from '@/stores/useCourseStore'
import { useDiscussionStore } from '@/stores/useDiscussionStore'

const route = useRoute()
const authStore = useAuthStore()
const courseStore = useCourseStore()
const discussionStore = useDiscussionStore()

const courseId = computed(() => {
  const id = route.params.id
  return typeof id === 'string' ? Number.parseInt(id, 10) : Number(id)
})

const course = computed(() => {
  const selected = courseStore.selectedCourse
  if (selected && selected.id === courseId.value) {
    const discussions = discussionStore.getDiscussions(selected.id)
    return {
      ...selected,
      comments: discussions.length > 0 ? discussions : (selected.comments ?? []),
    }
  }
  return null
})

async function loadData() {
  if (Number.isNaN(courseId.value))
    return
  await courseStore.fetchCourseById(courseId.value)
  await discussionStore.fetchDiscussions(courseId.value)
}

async function handleReply(payload: { parentId: number, content: string }) {
  if (Number.isNaN(courseId.value))
    return
  await discussionStore.addReply(
    courseId.value,
    payload.parentId,
    payload.content,
    authStore.displayName ?? undefined,
  )
}

async function handleSubmitReview(payload: {
  title: string
  content: string
  ratings: {
    gain: number
    highScore: number
    easiness: number
    teacherStyle: number
  }
}) {
  if (!courseStore.selectedCourse)
    return
  const selected = courseStore.selectedCourse
  const reviewCount = selected.summary?.reviewCount ?? 0
  const nextCount = reviewCount + 1
  const nextRatings = {
    gain: Number(((((selected.ratings?.gain ?? 0) * reviewCount) + payload.ratings.gain) / nextCount).toFixed(2)),
    highScore: Number(((((selected.ratings?.highScore ?? 0) * reviewCount) + payload.ratings.highScore) / nextCount).toFixed(2)),
    easiness: Number(((((selected.ratings?.easiness ?? 0) * reviewCount) + payload.ratings.easiness) / nextCount).toFixed(2)),
    teacherStyle: Number(((((selected.ratings?.teacherStyle ?? 0) * reviewCount) + payload.ratings.teacherStyle) / nextCount).toFixed(2)),
  }
  await discussionStore.submitDiscussion(courseId.value, {
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
      <CourseDetail
        :course="course"
        @reply="handleReply"
        @submit-review="handleSubmitReview"
      />
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
