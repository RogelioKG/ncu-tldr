import { describe, expect, it } from 'vitest'
import { courseReviewSchema } from '@/schemas'

describe('course review schema', () => {
  it('accepts payload with semester and at least one star', () => {
    const result = courseReviewSchema.safeParse({
      semester: '114-1',
      reward: 4,
      score: 0,
      easiness: 0,
      teacherStyle: 0,
      weeklyHours: 5,
      textbook: '',
      comment: '',
    })

    expect(result.success).toBe(true)
  })

  it('accepts payload with textbook only (no stars)', () => {
    const result = courseReviewSchema.safeParse({
      semester: '114-1',
      reward: 0,
      score: 0,
      easiness: 0,
      teacherStyle: 0,
      weeklyHours: 5,
      textbook: '自編講義',
      comment: '',
    })

    expect(result.success).toBe(true)
  })

  it('rejects missing semester', () => {
    const result = courseReviewSchema.safeParse({
      semester: '',
      reward: 4,
      score: 0,
      easiness: 0,
      teacherStyle: 0,
      weeklyHours: 5,
      textbook: '',
      comment: '',
    })

    expect(result.success).toBe(false)
    if (result.success) {
      return
    }

    const hasExpectedIssue = result.error.issues.some(issue =>
      issue.path[0] === 'semester' && issue.message === '請選擇修課學期',
    )
    expect(hasExpectedIssue).toBe(true)
  })

  it('rejects payload with no stars and no text', () => {
    const result = courseReviewSchema.safeParse({
      semester: '114-1',
      reward: 0,
      score: 0,
      easiness: 0,
      teacherStyle: 0,
      weeklyHours: 5,
      textbook: '',
      comment: '',
    })

    expect(result.success).toBe(false)
    if (result.success) {
      return
    }

    const hasExpectedIssue = result.error.issues.some(issue =>
      issue.path[0] === '_form' && issue.message === '請至少填寫一項評價內容',
    )
    expect(hasExpectedIssue).toBe(true)
  })

  it('rejects weeklyHours out of range', () => {
    const result = courseReviewSchema.safeParse({
      semester: '114-1',
      reward: 4,
      score: 0,
      easiness: 0,
      teacherStyle: 0,
      weeklyHours: 25,
      textbook: '',
      comment: '',
    })

    expect(result.success).toBe(false)
    if (result.success) {
      return
    }

    const hasExpectedIssue = result.error.issues.some(issue => issue.path[0] === 'weeklyHours')
    expect(hasExpectedIssue).toBe(true)
  })
})
