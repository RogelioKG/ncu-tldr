import type { CourseComment } from '@/types'
import { request } from './client'

interface RawComment {
  id: number
  user: string
  title: string
  content: string
  date: string
  likes: number
  dislikes: number
  parentId: number | null
  isDeleted?: boolean
  canDelete?: boolean
}

function normalizeComment(raw: RawComment): CourseComment {
  return {
    id: raw.id,
    user: raw.user,
    title: raw.title,
    content: raw.content,
    date: raw.date,
    likes: raw.likes,
    dislikes: raw.dislikes,
    parentId: raw.parentId ?? undefined,
    isDeleted: raw.isDeleted ?? false,
    canDelete: raw.canDelete ?? false,
  }
}

export interface CreateCommentPayload {
  content: string
  parentId?: number
}

export async function getComments(courseId: number): Promise<CourseComment[]> {
  const raw = await request<RawComment[]>(`/api/v1/courses/${courseId}/comments`)
  return raw.map(normalizeComment)
}

export async function createComment(
  courseId: number,
  payload: CreateCommentPayload,
): Promise<CourseComment> {
  const body: { content: string, parentId?: number } = {
    content: payload.content,
  }
  if (payload.parentId != null)
    body.parentId = payload.parentId

  const raw = await request<RawComment>(`/api/v1/courses/${courseId}/comments`, {
    method: 'POST',
    body: JSON.stringify(body),
  })
  return normalizeComment(raw)
}

export async function deleteComment(
  courseId: number,
  commentId: number,
): Promise<void> {
  await request<void>(`/api/v1/courses/${courseId}/comments/${commentId}`, {
    method: 'DELETE',
  })
}
