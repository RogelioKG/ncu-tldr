<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import CourseDetail from '@/components/CourseDetail.vue'
import { useCommentStore } from '@/stores/useCommentStore'
import { useCourseStore } from '@/stores/useCourseStore'
import { useReviewStore } from '@/stores/useReviewStore'

const route = useRoute()
const courseStore = useCourseStore()
const reviewStore = useReviewStore()
const commentStore = useCommentStore()

const courseId = computed(() => {
  const id = route.params.id
  return typeof id === 'string' ? Number.parseInt(id, 10) : Number(id)
})

const course = computed(() => courseStore.selectedCourse)
const reviews = computed(() => reviewStore.getCourseReviews(courseId.value))
const comments = computed(() => commentStore.getCourseComments(courseId.value))

async function loadData() {
  if (Number.isNaN(courseId.value))
    return
  await courseStore.fetchCourseById(courseId.value)
  await reviewStore.fetchReviews(courseId.value)
  await commentStore.fetchComments(courseId.value)
}

async function handleReply(payload: { parentId: number, content: string }) {
  if (Number.isNaN(courseId.value))
    return
  await commentStore.addReply(courseId.value, {
    content: payload.content,
    parentId: payload.parentId,
  })
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
  await reviewStore.submitReview(courseId.value, {
    title: payload.title,
    content: payload.content,
    ratings: payload.ratings,
  })
  courseStore.applyReviewRatings(courseId.value, nextRatings)
}

watch(courseId, loadData)
onMounted(loadData)
</script>

<template>
  <div class="course-detail-view">
    <div v-if="course">
      <CourseDetail
        :course="course"
        :reviews="reviews"
        :comments="comments"
        @reply="handleReply"
        @submit-review="handleSubmitReview"
      />
    </div>
    <div v-else class="not-found">
      <p>
        找不到該課程資訊。
      </p>
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
