import type { CourseComment, CourseRatings } from '@/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { hasBackendApi } from '@/api/client'
import { createComment, getComments } from '@/api/comments'
import { createReview, getReviews } from '@/api/reviews'

const DATE_DASH_REGEX = /-/g

export const useDiscussionStore = defineStore('discussion', () => {
  const discussionsByCourse = ref<Record<number, CourseComment[]>>({})
  const isLoading = ref(false)

  const totalDiscussionCount = computed(() =>
    Object.values(discussionsByCourse.value).reduce((sum, rows) => sum + rows.length, 0),
  )

  async function fetchDiscussions(courseId: number): Promise<void> {
    isLoading.value = true
    try {
      const rows = hasBackendApi()
        ? await getComments(courseId)
        : await getReviews(courseId)
      discussionsByCourse.value = {
        ...discussionsByCourse.value,
        [courseId]: rows,
      }
    }
    finally {
      isLoading.value = false
    }
  }

  function getDiscussions(courseId: number): CourseComment[] {
    return discussionsByCourse.value[courseId] ?? []
  }

  async function submitDiscussion(
    courseId: number,
    payload: {
      user: string
      title: string
      content: string
      ratings: CourseRatings
    },
  ): Promise<CourseComment> {
    const created = await createReview(courseId, payload)
    const enriched: CourseComment = {
      ...created,
      ratings: payload.ratings,
    }
    const current = discussionsByCourse.value[courseId] ?? []
    discussionsByCourse.value = {
      ...discussionsByCourse.value,
      [courseId]: [...current, enriched],
    }
    return enriched
  }

  async function addReply(
    courseId: number,
    parentId: number,
    content: string,
    user?: string,
  ): Promise<CourseComment> {
    if (hasBackendApi()) {
      const created = await createComment(courseId, { content, parentId })
      const current = discussionsByCourse.value[courseId] ?? []
      discussionsByCourse.value = {
        ...discussionsByCourse.value,
        [courseId]: [...current, created],
      }
      return created
    }
    const current = discussionsByCourse.value[courseId] ?? []
    const nextId = current.reduce((max, c) => Math.max(max, c.id), 0) + 1
    const created: CourseComment = {
      id: nextId,
      user: user ?? '匿名同學',
      title: content.slice(0, 50),
      content,
      date: new Date().toISOString().slice(0, 10).replace(DATE_DASH_REGEX, '/'),
      likes: 0,
      dislikes: 0,
      parentId,
    }
    discussionsByCourse.value = {
      ...discussionsByCourse.value,
      [courseId]: [...current, created],
    }
    return created
  }

  return {
    addReply,
    discussionsByCourse,
    fetchDiscussions,
    getDiscussions,
    isLoading,
    submitDiscussion,
    totalDiscussionCount,
  }
})
