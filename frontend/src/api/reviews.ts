import type { CourseComment, CourseRatings } from '@/types'
import { request } from './client'

export interface CreateReviewPayload {
  user: string
  title: string
  content: string
  ratings: CourseRatings
}

export async function getReviews(courseId: number): Promise<CourseComment[]> {
  return await request<CourseComment[]>(`/api/courses/${courseId}/reviews`)
}

export async function createReview(courseId: number, payload: CreateReviewPayload): Promise<CourseComment> {
  return await request<CourseComment>(`/api/courses/${courseId}/reviews`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
