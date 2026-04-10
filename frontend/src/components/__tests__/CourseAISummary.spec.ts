import type { CourseSummary } from '@/types'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import CourseAISummary from '../CourseAISummary.vue'
import CourseReviewForm from '../CourseReviewForm.vue'

const mockSummary: CourseSummary = {
  overview: '這是一門基礎課程',
  targetAudience: '資工系學生',
  textbook: '資料結構與演算法',
  prerequisites: '程式設計基礎',
  weeklyHours: '5-8 小時',
  gradingItems: [
    { label: '作業', percentage: 30 },
    { label: '期中考', percentage: 30 },
    { label: '期末考', percentage: 40 },
  ],
  notes: '作業較多，需要投入時間',
  reviewCount: 42,
}

describe('courseAISummary', () => {
  it('renders title when summary exists', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: mockSummary },
    })
    expect(wrapper.text()).toContain('AI 統整摘要')
  })

  it('renders review count', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: mockSummary },
    })
    expect(wrapper.text()).toContain('以下統整來自 42 則評價')
  })

  it('renders review action button when summary exists', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: mockSummary },
    })
    expect(wrapper.find('.ai-summary__action-btn').exists()).toBe(true)
  })

  it('renders overview', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: mockSummary },
    })
    expect(wrapper.text()).toContain('這是一門基礎課程')
  })

  it('renders target audience', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: mockSummary },
    })
    expect(wrapper.text()).toContain('資工系學生')
  })

  it('renders textbook', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: mockSummary },
    })
    expect(wrapper.text()).toContain('資料結構與演算法')
  })

  it('renders prerequisites', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: mockSummary },
    })
    expect(wrapper.text()).toContain('程式設計基礎')
  })

  it('renders weekly hours', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: mockSummary },
    })
    expect(wrapper.text()).toContain('5-8 小時')
  })

  it('renders notes', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: mockSummary },
    })
    expect(wrapper.text()).toContain('作業較多，需要投入時間')
  })

  it('renders grading pie chart', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: mockSummary },
    })
    expect(wrapper.find('.ai-summary__chart').exists()).toBe(true)
  })

  it('shows empty state when no summary', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: undefined },
    })
    expect(wrapper.text()).toContain('尚無評價')
    expect(wrapper.text()).toContain('你是第一個留下修課經驗的人')
  })

  it('renders write review button in empty state', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: undefined },
    })
    expect(wrapper.find('.ai-summary__empty-btn').exists()).toBe(true)
    expect(wrapper.text()).toContain('撰寫評價')
  })

  it('renders empty state image', () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: undefined },
    })
    const img = wrapper.find('.ai-summary__empty-icon')
    expect(img.exists()).toBe(true)
  })

  it('opens review form and emits submit-review', async () => {
    const wrapper = mount(CourseAISummary, {
      props: { summary: mockSummary, courseName: '資料結構' },
    })
    await wrapper.get('.ai-summary__action-btn').trigger('click')
    const form = wrapper.findComponent(CourseReviewForm)
    expect(form.exists()).toBe(true)
    form.vm.$emit('submit', {
      title: '[114-1] 資料結構',
      content: '內容',
      ratings: { gain: 5, highScore: 4, easiness: 3, teacherStyle: 4 },
      weeklyHours: '5h',
      textbook: '講義',
      semester: '114-1',
    })
    expect(wrapper.emitted('submitReview')).toBeTruthy()
  })
})
