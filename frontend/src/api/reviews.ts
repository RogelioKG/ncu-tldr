import type { CourseComment, CourseRatings } from '@/types'
import { request } from './client'

interface RawReview {
  id: number
  user: string
  title: string
  content: string | null
  date: string
  likes: number
  dislikes: number
  parentId: number | null
  ratings: {
    gain: number | null
    highScore: number | null
    easiness: number | null
    teacherStyle: number | null
  } | null
  semester: string | null
  weeklyHours: number | null
  textbook: string | null
}

function normalizeReview(raw: RawReview): CourseComment {
  return {
    id: raw.id,
    user: raw.user,
    title: raw.title,
    content: raw.content ?? '',
    date: raw.date,
    likes: raw.likes,
    dislikes: raw.dislikes,
    parentId: raw.parentId ?? undefined,
    ratings: raw.ratings ?? undefined,
  }
}

export interface SubmitReviewInput {
  semester: string
  title: string
  content: string | null
  ratings: CourseRatings | null
  weeklyHours: number | null
  textbook: string | null
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
      semester: payload.semester,
      title: payload.title,
      content: payload.content,
      ratings: payload.ratings,
      weeklyHours: payload.weeklyHours,
      textbook: payload.textbook,
    }),
    token,
  })
  return normalizeReview(raw)
}
