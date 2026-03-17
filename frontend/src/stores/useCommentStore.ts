import type { CourseComment } from '@/types'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { createComment, getComments } from '@/api/comments'

export const useCommentStore = defineStore('comment', () => {
  const commentsByCourse = ref<Record<number, CourseComment[]>>({})
  const isLoading = ref(false)

  async function fetchComments(courseId: number): Promise<void> {
    isLoading.value = true
    try {
      const rows = await getComments(courseId)
      commentsByCourse.value = {
        ...commentsByCourse.value,
        [courseId]: rows,
      }
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
    parentId: number,
    content: string,
  ): Promise<CourseComment> {
    const created = await createComment(courseId, { content, parentId })
    const current = commentsByCourse.value[courseId] ?? []
    commentsByCourse.value = {
      ...commentsByCourse.value,
      [courseId]: [...current, created],
    }
    return created
  }

  return {
    addReply,
    commentsByCourse,
    fetchComments,
    getCourseComments,
    isLoading,
  }
})
