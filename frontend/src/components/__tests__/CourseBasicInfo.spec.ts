import type { Course } from '@/types'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import CourseBasicInfo from '../CourseBasicInfo.vue'

const mockCourse: Course = {
  id: 1,
  name: '資料結構',
  teacher: '王小明',
  tags: ['必修'],
  ratings: { gain: 4.5, highScore: 4.0, easiness: 3.5, teacherStyle: 4.2 },
  department: '資訊工程學系',
  code: 'CS101',
  time: '週一 3-4',
  credits: 3,
  type: '必修',
}

describe('courseBasicInfo', () => {
  it('renders title', () => {
    const wrapper = mount(CourseBasicInfo, {
      props: { course: mockCourse },
    })
    expect(wrapper.text()).toContain('課程基本資訊')
  })

  it('renders school department', () => {
    const wrapper = mount(CourseBasicInfo, {
      props: { course: mockCourse },
    })
    expect(wrapper.text()).toContain('資訊工程學系')
  })

  it('renders course code', () => {
    const wrapper = mount(CourseBasicInfo, {
      props: { course: mockCourse },
    })
    expect(wrapper.text()).toContain('CS101')
  })

  it('renders teacher name', () => {
    const wrapper = mount(CourseBasicInfo, {
      props: { course: mockCourse },
    })
    expect(wrapper.text()).toContain('王小明')
  })

  it('renders course time', () => {
    const wrapper = mount(CourseBasicInfo, {
      props: { course: mockCourse },
    })
    expect(wrapper.text()).toContain('週一 3-4')
  })

  it('renders credits', () => {
    const wrapper = mount(CourseBasicInfo, {
      props: { course: mockCourse },
    })
    expect(wrapper.text()).toContain('3')
  })

  it('renders course type', () => {
    const wrapper = mount(CourseBasicInfo, {
      props: { course: mockCourse },
    })
    expect(wrapper.text()).toContain('必修')
  })

  it('displays dash for missing optional fields', () => {
    const courseWithoutOptional: Course = {
      id: 1,
      name: '資料結構',
      teacher: '王小明',
      tags: ['必修'],
      ratings: { gain: 4.5, highScore: 4.0, easiness: 3.5, teacherStyle: 4.2 },
    }
    const wrapper = mount(CourseBasicInfo, {
      props: { course: courseWithoutOptional },
    })
    expect(wrapper.text()).toContain('—')
  })
})
