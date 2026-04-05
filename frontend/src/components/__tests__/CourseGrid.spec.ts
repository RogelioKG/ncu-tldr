import type { Course } from '@/types'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'
import CourseGrid from '../CourseGrid.vue'

const mockCourses: Course[] = [
  {
    id: 1,
    name: '資料結構',
    teacher: '王小明',
    tags: ['必修'],
    ratings: { reward: 4.5, score: 4.0, easiness: 3.5, teacherStyle: 4.2 },
  },
  {
    id: 2,
    name: '演算法',
    teacher: '李大華',
    tags: ['選修'],
    ratings: { reward: 4.0, score: 3.5, easiness: 3.0, teacherStyle: 4.0 },
  },
]

describe('courseGrid', () => {
  it('renders all courses', () => {
    const wrapper = mount(CourseGrid, {
      props: { courses: mockCourses },
      global: { plugins: [createPinia()] },
    })
    expect(wrapper.findAll('.course-card').length).toBe(2)
  })

  it('renders empty grid when no courses', () => {
    const wrapper = mount(CourseGrid, {
      props: { courses: [] },
      global: { plugins: [createPinia()] },
    })
    expect(wrapper.findAll('.course-card').length).toBe(0)
  })

  it('emits select-course event when course is selected', async () => {
    const wrapper = mount(CourseGrid, {
      props: { courses: mockCourses },
      global: { plugins: [createPinia()] },
    })
    const cards = wrapper.findAll('.course-card')
    expect(cards.length).toBeGreaterThan(0)

    const firstCard = cards[0]!
    await firstCard.trigger('click')
    expect(wrapper.emitted('selectCourse')).toBeTruthy()
    expect(wrapper.emitted('selectCourse')?.[0]).toEqual([mockCourses[0]])
  })

  it('has correct grid layout class', () => {
    const wrapper = mount(CourseGrid, {
      props: { courses: mockCourses },
      global: { plugins: [createPinia()] },
    })
    expect(wrapper.find('.course-grid').exists()).toBe(true)
  })
})
