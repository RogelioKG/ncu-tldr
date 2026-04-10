import { z } from 'zod'

/**
 * 星等評分 (0-5)
 */
const starRating = z.number().int().min(0).max(5)

/**
 * 課程評價表單驗證 Schema
 */
export const courseReviewSchema = z.object({
  semester: z.string().min(1, '請選擇修課學期'),
  gain: starRating,
  highScore: starRating,
  easiness: starRating,
  teacherStyle: starRating,
  weeklyHours: z.number().min(1).max(20),
  textbook: z.string().max(100, '教科書欄位最多 100 字').optional(),
  comment: z.string().max(1000, '評論最多 1000 字').optional(),
}).refine((data) => {
  // 至少要填一項評價內容（星等、教科書或評論）
  const hasStars = data.gain > 0 || data.highScore > 0 || data.easiness > 0 || data.teacherStyle > 0
  const hasTextbook = (data.textbook?.trim().length ?? 0) > 0
  const hasComment = (data.comment?.trim().length ?? 0) > 0
  return hasStars || hasTextbook || hasComment
}, {
  message: '請至少填寫一項評價內容',
  path: ['_form'],
})

/**
 * TypeScript 型別推導
 */
export type CourseReviewInput = z.infer<typeof courseReviewSchema>
