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

async function handleDeleteComment(payload: { commentId: number }) {
  if (Number.isNaN(courseId.value))
    return
  await commentStore.removeComment(courseId.value, payload.commentId)
}

async function handleSubmitReview(payload: {
  semester: string
  title: string
  content: string | null
  ratings: {
    gain: number
    highScore: number
    easiness: number
    teacherStyle: number
  } | null
  weeklyHours: number | null
  textbook: string | null
}) {
  if (!courseStore.selectedCourse)
    return
  const selected = courseStore.selectedCourse
  if (payload.ratings) {
    const reviewCount = selected.summary?.reviewCount ?? 0
    const nextCount = reviewCount + 1
    const nextRatings = {
      gain: Number(((((selected.ratings?.gain ?? 0) * reviewCount) + payload.ratings.gain) / nextCount).toFixed(2)),
      highScore: Number(((((selected.ratings?.highScore ?? 0) * reviewCount) + payload.ratings.highScore) / nextCount).toFixed(2)),
      easiness: Number(((((selected.ratings?.easiness ?? 0) * reviewCount) + payload.ratings.easiness) / nextCount).toFixed(2)),
      teacherStyle: Number(((((selected.ratings?.teacherStyle ?? 0) * reviewCount) + payload.ratings.teacherStyle) / nextCount).toFixed(2)),
    }
    courseStore.applyReviewRatings(courseId.value, nextRatings)
  }
  await reviewStore.submitReview(courseId.value, {
    semester: payload.semester,
    title: payload.title,
    content: payload.content,
    ratings: payload.ratings,
    weeklyHours: payload.weeklyHours,
    textbook: payload.textbook,
  })
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
        @delete-comment="handleDeleteComment"
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
