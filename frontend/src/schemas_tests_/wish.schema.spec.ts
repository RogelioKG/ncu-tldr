import { describe, expect, it } from 'vitest'
import { wishFormSchema } from '@/schemas'

describe('wish form schema', () => {
  it('accepts valid wish payload', () => {
    const result = wishFormSchema.safeParse({
      name: '資料結構',
      teacher: '王大明',
    })

    expect(result.success).toBe(true)
  })

  it('rejects empty course name', () => {
    const result = wishFormSchema.safeParse({
      name: '',
      teacher: '王大明',
    })

    expect(result.success).toBe(false)
    if (result.success) {
      return
    }

    const hasExpectedIssue = result.error.issues.some(issue =>
      issue.path[0] === 'name' && issue.message === '請輸入課程名稱',
    )
    expect(hasExpectedIssue).toBe(true)
  })

  it('rejects too long teacher name', () => {
    const result = wishFormSchema.safeParse({
      name: '資料結構',
      teacher: 'a'.repeat(51),
    })

    expect(result.success).toBe(false)
    if (result.success) {
      return
    }

    const hasExpectedIssue = result.error.issues.some(issue =>
      issue.path[0] === 'teacher' && issue.message === '教師姓名最多 50 字',
    )
    expect(hasExpectedIssue).toBe(true)
  })
})
