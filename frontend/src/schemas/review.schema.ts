import { z } from 'zod'

const starRating = z.number().int().min(0).max(5)

export const courseReviewSchema = z.object({
  semester: z.string().min(1, '請選擇修課學期'),
  gain: starRating,
  highScore: starRating,
  easiness: starRating,
  teacherStyle: starRating,
  weeklyHours: z.number().min(1).max(20),
  textbook: z.string().max(100, '教科書欄位最多 100 字').optional(),
  comment: z.string().max(1000, '評論最多 1000 字').optional(),
})

export type CourseReviewInput = z.infer<typeof courseReviewSchema>
