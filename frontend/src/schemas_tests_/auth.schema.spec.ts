import { describe, expect, it } from 'vitest'
import { loginSchema, registerSchema } from '@/schemas'

describe('auth schema', () => {
  it('accepts valid login payload', () => {
    const result = loginSchema.safeParse({
      email: '111223333@cc.ncu.edu.tw',
      password: 'hello123',
    })

    expect(result.success).toBe(true)
  })

  it('rejects empty login email', () => {
    const result = loginSchema.safeParse({
      email: '',
      password: 'hello123',
    })

    expect(result.success).toBe(false)
    if (result.success) {
      return
    }

    expect(result.error.issues[0]?.message).toBe('請輸入電子信箱')
  })

  it('accepts valid register payload', () => {
    const result = registerSchema.safeParse({
      email: '111223333@cc.ncu.edu.tw',
      password: 'Abcdef12!',
      confirmPassword: 'Abcdef12!',
    })

    expect(result.success).toBe(true)
  })

  it('rejects non-NCU email on register', () => {
    const result = registerSchema.safeParse({
      email: 'student@gmail.com',
      password: 'Abcdef12!',
      confirmPassword: 'Abcdef12!',
    })

    expect(result.success).toBe(false)
    if (result.success) {
      return
    }

    const hasExpectedIssue = result.error.issues.some(issue =>
      issue.path[0] === 'email' && issue.message === '請使用正確的學校信箱（9 碼學號 @cc.ncu.edu.tw）',
    )
    expect(hasExpectedIssue).toBe(true)
  })

  it('rejects mismatched confirm password', () => {
    const result = registerSchema.safeParse({
      email: '111223333@cc.ncu.edu.tw',
      password: 'Abcdef12!',
      confirmPassword: 'Abcdef12@',
    })

    expect(result.success).toBe(false)
    if (result.success) {
      return
    }

    const hasExpectedIssue = result.error.issues.some(issue =>
      issue.path[0] === 'confirmPassword' && issue.message === '密碼與確認密碼不一致',
    )
    expect(hasExpectedIssue).toBe(true)
  })
})
