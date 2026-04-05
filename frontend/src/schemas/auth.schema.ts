import { z } from 'zod'

/**
 * NCU 學生信箱格式驗證
 * 格式：9碼學號@cc.ncu.edu.tw
 */
const ncuEmailRegex = /^\d{9}@cc\.ncu\.edu\.tw$/

/**
 * 登入表單驗證 Schema
 */
export const loginSchema = z.object({
  email: z.string()
    .min(1, '請輸入電子信箱')
    .email('請輸入有效的電子信箱格式'),
  password: z.string()
    .min(1, '請輸入密碼'),
})

/**
 * 註冊表單驗證 Schema
 * 包含密碼強度要求：至少 8 字元、需包含大小寫字母、數字及特殊符號
 */
export const registerSchema = z.object({
  email: z.string()
    .min(1, '請輸入電子信箱')
    .regex(ncuEmailRegex, '請使用正確的學校信箱（9 碼學號 @cc.ncu.edu.tw）'),
  password: z.string()
    .min(8, '密碼長度至少需要 8 個字元')
    .regex(/[a-z]/, '密碼需包含至少一個小寫字母')
    .regex(/[A-Z]/, '密碼需包含至少一個大寫字母')
    .regex(/\d/, '密碼需包含至少一個數字')
    .regex(/[\W_]/, '密碼需包含至少一個特殊符號'),
  confirmPassword: z.string()
    .min(1, '請確認密碼'),
}).refine(data => data.password === data.confirmPassword, {
  message: '密碼與確認密碼不一致',
  path: ['confirmPassword'],
})

/**
 * TypeScript 型別推導
 */
export type LoginInput = z.infer<typeof loginSchema>
export type RegisterInput = z.infer<typeof registerSchema>
