import type { Course } from '@/types'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'
import CourseCard from '../CourseCard.vue'

const mockCourse: Course = {
  id: 1,
  name: '資料結構',
  teacher: '王小明',
  tags: ['必修', '程式設計'],
  ratings: {
    gain: 4.5,
    highScore: 4.0,
    easiness: 3.5,
    teacherStyle: 4.2,
  },
}

function mountCard(course: Course) {
  return mount(CourseCard, {
    props: { course },
    global: { plugins: [createPinia()] },
  })
}

describe('courseCard', () => {
  it('renders course name', () => {
    const wrapper = mountCard(mockCourse)
    expect(wrapper.text()).toContain('資料結構')
  })

  it('renders teacher name', () => {
    const wrapper = mountCard(mockCourse)
    expect(wrapper.text()).toContain('教師：王小明')
  })

  it('renders ratings section with four categories', () => {
    const wrapper = mountCard(mockCourse)
    const ratingsEl = wrapper.find('.course-card__ratings')
    expect(ratingsEl.exists()).toBe(true)
    expect(wrapper.text()).toContain('收穫')
    expect(wrapper.text()).toContain('分數')
    expect(wrapper.text()).toContain('輕鬆')
    expect(wrapper.text()).toContain('教師風格')
  })

  it('renders tags', () => {
    const wrapper = mountCard(mockCourse)
    expect(wrapper.text()).toContain('#必修')
    expect(wrapper.text()).toContain('#程式設計')
  })

  it('renders full long course name via CSS truncation', () => {
    const longNameCourse = { ...mockCourse, name: '這是一個非常長的課程名稱' }
    const wrapper = mountCard(longNameCourse)
    expect(wrapper.text()).toContain('這是一個非常長的課程名稱')
  })

  it('emits select event when clicked', async () => {
    const wrapper = mountCard(mockCourse)
    await wrapper.trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')?.[0]).toEqual([mockCourse])
  })

  it('applies hover class on mouseenter', async () => {
    const wrapper = mountCard(mockCourse)
    await wrapper.trigger('mouseenter')
    expect(wrapper.classes()).toContain('course-card--hovered')
  })

  it('removes hover class on mouseleave', async () => {
    const wrapper = mountCard(mockCourse)
    await wrapper.trigger('mouseenter')
    await wrapper.trigger('mouseleave')
    expect(wrapper.classes()).not.toContain('course-card--hovered')
  })

  it('renders all rating categories', () => {
    const wrapper = mountCard(mockCourse)
    expect(wrapper.text()).toContain('收穫')
    expect(wrapper.text()).toContain('分數')
    expect(wrapper.text()).toContain('輕鬆')
    expect(wrapper.text()).toContain('教師風格')
  })
})
