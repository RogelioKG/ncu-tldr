import type { WishCourse } from '@/types'
import { request } from './client'

interface WishCourseRaw {
  course_id: number
  title: string
  vote_count: number
  has_voted: boolean
}

function toWishCourse(raw: WishCourseRaw): WishCourse {
  return {
    courseId: raw.course_id,
    title: raw.title,
    voteCount: raw.vote_count,
    hasVoted: raw.has_voted,
  }
}

export async function getWishlist(): Promise<WishCourse[]> {
  const data = await request<WishCourseRaw[]>('/api/v1/wishlist')
  return data.map(toWishCourse)
}

export async function voteForCourse(courseId: number, token: string): Promise<void> {
  await request<void>(`/api/v1/wishlist/${courseId}`, { method: 'POST', token })
}

export async function unvoteForCourse(courseId: number, token: string): Promise<void> {
  await request<void>(`/api/v1/wishlist/${courseId}`, { method: 'DELETE', token })
}
