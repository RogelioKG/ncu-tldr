import type { CreateCommentPayload } from '@/api/comments'
import type { ReactionType } from '@/api/likes'
import type { CourseComment } from '@/types'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createComment, getComments } from '@/api/comments'
import { reactToComment } from '@/api/likes'
import { useAuthStore } from '@/stores/useAuthStore'

export const useCommentStore = defineStore('comment', () => {
  const commentsByCourse = ref<Record<number, CourseComment[]>>({})
  const isLoading = ref(false)

  async function fetchComments(courseId: number): Promise<void> {
    isLoading.value = true
    try {
      const rows = await getComments(courseId)
      commentsByCourse.value = { ...commentsByCourse.value, [courseId]: rows }
    }
    finally {
      isLoading.value = false
    }
  }

  function getCourseComments(courseId: number): CourseComment[] {
    return commentsByCourse.value[courseId] ?? []
  }

  async function addReply(
    courseId: number,
    payload: CreateCommentPayload,
  ): Promise<CourseComment> {
    const authStore = useAuthStore()
    const token = authStore.token
    if (!token)
      throw new Error('登入後才能留言')

    const created = await createComment(courseId, payload, token)
    const current = commentsByCourse.value[courseId] ?? []
    commentsByCourse.value = {
      ...commentsByCourse.value,
      [courseId]: [...current, created],
    }
    return created
  }

  async function reactToItem(courseId: number, commentId: number, reaction: ReactionType): Promise<void> {
    const current = commentsByCourse.value[courseId] ?? []
    commentsByCourse.value = {
      ...commentsByCourse.value,
      [courseId]: current.map(c =>
        c.id !== commentId
          ? c
          : {
              ...c,
              likes: reaction === 'like' ? c.likes + 1 : c.likes,
              dislikes: reaction === 'dislike' ? c.dislikes + 1 : c.dislikes,
            },
      ),
    }
    const authStore = useAuthStore()
    await reactToComment(courseId, commentId, reaction, authStore.token ?? undefined)
  }

  return {
    addReply,
    commentsByCourse,
    fetchComments,
    getCourseComments,
    isLoading,
    reactToItem,
  }
})
