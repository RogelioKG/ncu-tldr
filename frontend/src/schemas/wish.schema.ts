import { z } from 'zod'

/**
 * 許願池表單驗證 Schema
 */
export const wishFormSchema = z.object({
  name: z.string()
    .min(1, '請輸入課程名稱')
    .max(100, '課程名稱最多 100 字'),
  teacher: z.string()
    .min(1, '請輸入教師姓名')
    .max(50, '教師姓名最多 50 字'),
})

/**
 * TypeScript 型別推導
 */
export type WishFormInput = z.infer<typeof wishFormSchema>
