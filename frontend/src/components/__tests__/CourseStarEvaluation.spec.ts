import type { CourseRatings } from '@/types'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import CourseStarEvaluation from '../CourseStarEvaluation.vue'

const mockRatings: CourseRatings = {
  reward: 4.5,
  score: 4.0,
  easiness: 3.5,
  teacherStyle: 4.2,
}

describe('courseStarEvaluation', () => {
  it('renders title', () => {
    const wrapper = mount(CourseStarEvaluation, {
      props: { ratings: mockRatings },
    })
    expect(wrapper.text()).toContain('星星評價')
  })

  it('calculates weighted overall rating correctly', () => {
    const wrapper = mount(CourseStarEvaluation, {
      props: { ratings: mockRatings },
    })
    const expected = (4.5 * 0.35 + 4.0 * 0.2 + 3.5 * 0.15 + 4.2 * 0.3).toFixed(1)
    expect(wrapper.text()).toContain(expected)
  })

  it('renders all rating metrics', () => {
    const wrapper = mount(CourseStarEvaluation, {
      props: { ratings: mockRatings },
    })
    expect(wrapper.text()).toContain('收穫')
    expect(wrapper.text()).toContain('分數')
    expect(wrapper.text()).toContain('輕鬆')
    expect(wrapper.text()).toContain('教師風格')
  })

  it('clamps ratings above 5', () => {
    const highRatings: CourseRatings = {
      reward: 6.0,
      score: 5.5,
      easiness: 7.0,
      teacherStyle: 5.2,
    }
    const wrapper = mount(CourseStarEvaluation, {
      props: { ratings: highRatings },
    })
    // Should clamp to max 5
    expect(wrapper.text()).toContain('5')
    expect(wrapper.text()).toContain('/ 5')
  })

  it('clamps ratings below 0', () => {
    const lowRatings: CourseRatings = {
      reward: -1.0,
      score: -0.5,
      easiness: -2.0,
      teacherStyle: -0.2,
    }
    const wrapper = mount(CourseStarEvaluation, {
      props: { ratings: lowRatings },
    })
    // Should clamp to min 0
    expect(wrapper.text()).toContain('0')
    expect(wrapper.text()).toContain('/ 5')
  })

  it('renders all four rating metrics in metrics section', () => {
    const wrapper = mount(CourseStarEvaluation, {
      props: { ratings: mockRatings },
    })
    const metrics = wrapper.find('.rating-card__metrics')
    expect(metrics.exists()).toBe(true)
    expect(wrapper.text()).toContain('收穫')
    expect(wrapper.text()).toContain('分數')
    expect(wrapper.text()).toContain('輕鬆')
    expect(wrapper.text()).toContain('教師風格')
  })

  it('renders subtitle', () => {
    const wrapper = mount(CourseStarEvaluation, {
      props: { ratings: mockRatings },
    })
    expect(wrapper.text()).toContain('經使用者可信度加權平均')
  })
})
