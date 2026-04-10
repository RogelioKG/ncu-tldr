import type { CourseComment, CourseRatings } from '@/types'
import { request } from './client'

interface RawReview {
  id: number
  user: string
  title: string
  content: string
  date: string
  likes: number
  dislikes: number
  parentId: number | null
  ratings: {
    gain: number
    highScore: number
    easiness: number
    teacherStyle: number
  } | null
}

function normalizeReview(raw: RawReview): CourseComment {
  return {
    id: raw.id,
    user: raw.user,
    title: raw.title,
    content: raw.content,
    date: raw.date,
    likes: raw.likes,
    dislikes: raw.dislikes,
    parentId: raw.parentId ?? undefined,
    ratings: raw.ratings ?? undefined,
  }
}

export interface SubmitReviewInput {
  title: string
  content: string
  ratings: CourseRatings
}

export async function getReviews(courseId: number): Promise<CourseComment[]> {
  const raw = await request<RawReview[]>(`/api/v1/courses/${courseId}/reviews`)
  return raw.map(normalizeReview)
}

export async function createReview(
  courseId: number,
  payload: SubmitReviewInput,
  token: string,
): Promise<CourseComment> {
  const raw = await request<RawReview>(`/api/v1/courses/${courseId}/reviews`, {
    method: 'POST',
    body: JSON.stringify({
      title: payload.title,
      content: payload.content,
      ratings: payload.ratings,
    }),
    token,
  })
  return normalizeReview(raw)
}
