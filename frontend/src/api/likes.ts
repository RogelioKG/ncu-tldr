// Stub — waiting for backend to implement like/dislike endpoints.
// See docs/backend-requirements.md for the expected API contract.

export type ReactionType = 'like' | 'dislike'

export interface ReactionResult {
  likes: number
  dislikes: number
}

/**
 * Like or dislike a review.
 * @throws {Error} always — endpoint not yet implemented on backend.
 */
export async function reactToReview(
  _courseId: number,
  _reviewId: number,
  _reaction: ReactionType,
  _token?: string,
): Promise<ReactionResult> {
  throw new Error('Like/dislike API not yet implemented. See docs/backend-requirements.md.')
}

/**
 * Like or dislike a comment.
 * @throws {Error} always — endpoint not yet implemented on backend.
 */
export async function reactToComment(
  _courseId: number,
  _commentId: number,
  _reaction: ReactionType,
  _token?: string,
): Promise<ReactionResult> {
  throw new Error('Like/dislike API not yet implemented. See docs/backend-requirements.md.')
}
