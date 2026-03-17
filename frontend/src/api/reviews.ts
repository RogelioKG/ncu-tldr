import type { CourseComment, CourseRatings } from '@/types'
import { mockCourses } from '@/mock/courses'
import { hasBackendApi, request } from './client'

export interface CreateReviewPayload {
  user: string
  title: string
  content: string
  ratings: CourseRatings
}

export async function getReviews(courseId: number): Promise<CourseComment[]> {
  if (hasBackendApi()) {
    return await request<CourseComment[]>(`/api/courses/${courseId}/reviews`)
  }
  const course = mockCourses.find(row => row.id === courseId)
  return course?.comments ? [...course.comments] : []
}

export async function createReview(courseId: number, payload: CreateReviewPayload): Promise<CourseComment> {
  if (hasBackendApi()) {
    return await request<CourseComment>(`/api/courses/${courseId}/reviews`, {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }
  const course = mockCourses.find(row => row.id === courseId)
  const nextId = (course?.comments ?? []).reduce((maxId, row) => Math.max(maxId, row.id), 0) + 1
  return {
    id: nextId,
    user: payload.user,
    title: payload.title,
    content: payload.content,
    date: new Date().toISOString().slice(0, 10),
    likes: 0,
    dislikes: 0,
  }
}
