import type { CourseComment } from '@/types'
import { hasBackendApi, request } from './client'

export interface CreateCommentPayload {
  content: string
  title?: string
  parentId?: number
}

export async function getComments(courseId: number): Promise<CourseComment[]> {
  if (!hasBackendApi())
    return []
  const raw = await request<Array<CourseComment & { parentId?: number }>>(
    `/api/courses/${courseId}/comments`,
  )
  return raw.map(row => ({
    id: row.id,
    user: row.user,
    title: row.title ?? row.content.slice(0, 50),
    content: row.content,
    date: row.date,
    likes: row.likes,
    dislikes: row.dislikes,
    parentId: row.parentId,
  }))
}

export async function createComment(
  courseId: number,
  payload: CreateCommentPayload,
): Promise<CourseComment> {
  const body: { content: string, title?: string, parentId?: number } = {
    content: payload.content,
  }
  if (payload.title != null)
    body.title = payload.title
  if (payload.parentId != null)
    body.parentId = payload.parentId
  const created = await request<CourseComment & { parentId?: number }>(
    `/api/courses/${courseId}/comments`,
    {
      method: 'POST',
      body: JSON.stringify(body),
    },
  )
  return {
    id: created.id,
    user: created.user,
    title: created.title ?? created.content.slice(0, 50),
    content: created.content,
    date: created.date,
    likes: created.likes,
    dislikes: created.dislikes,
    parentId: created.parentId,
  }
}
