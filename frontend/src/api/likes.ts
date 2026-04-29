import { request } from './client'

export type ReactionType = 'like' | 'dislike'

export interface ReactionResult {
  likes: number
  dislikes: number
  userReaction: 'like' | 'dislike' | null
}

export async function reactToReview(
  _courseId: number,
  _reviewId: number,
  _reaction: ReactionType,
): Promise<ReactionResult> {
  throw new Error('Like/dislike for reviews not yet implemented.')
}

export async function reactToComment(
  courseId: number,
  commentId: number,
  reaction: ReactionType,
): Promise<ReactionResult> {
  return request<ReactionResult>(
    `/api/v1/courses/${courseId}/comments/${commentId}/react`,
    {
      method: 'POST',
      body: JSON.stringify({ reaction }),
    },
  )
}
