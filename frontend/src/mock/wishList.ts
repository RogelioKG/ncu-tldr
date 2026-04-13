/**
 * 許願池假資料（開發/展示用）
 */
import type { WishCourse } from '@/types'

export const mockWishList: WishCourse[] = [
  { courseId: 1, title: '演算法', voteCount: 5, hasVoted: false },
  { courseId: 2, title: '動力學', voteCount: 3, hasVoted: false },
  { courseId: 3, title: '當代潮流與兩性探討', voteCount: 2, hasVoted: false },
  { courseId: 4, title: '神鵰培養概論', voteCount: 1, hasVoted: false },
  { courseId: 5, title: '宮廟概論', voteCount: 1, hasVoted: false },
]
