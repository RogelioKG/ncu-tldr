import type { Course } from '@/types'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'
import CourseAISummary from '../CourseAISummary.vue'
import CourseBasicInfo from '../CourseBasicInfo.vue'
import CourseComments from '../CourseComments.vue'
import CourseDetail from '../CourseDetail.vue'
import CourseStarEvaluation from '../CourseStarEvaluation.vue'

const mockCourse: Course = {
  id: 1,
  name: '資料結構',
  teacher: '王小明',
  tags: ['必修', '程式設計', '資工系'],
  ratings: { reward: 4.5, score: 4.0, easiness: 3.5, teacherStyle: 4.2 },
  department: '資訊工程學系',
  code: 'CS101',
  time: '週一 3-4',
  credits: 3,
  type: '必修',
  summary: {
    overview: '基礎課程',
    targetAudience: '資工系學生',
    textbook: '資料結構',
    prerequisites: '程式設計',
    weeklyHours: '5-8小時',
    gradingItems: [{ label: '作業', percentage: 30 }],
    notes: '作業多',
    reviewCount: 10,
  },
  comments: [
    {
      id: 1,
      user: '匿名',
      title: '很棒',
      content: '很好',
      date: '2024-01-01',
      likes: 5,
      dislikes: 0,
    },
  ],
}

describe('courseDetail', () => {
  function mountCourseDetail(course: Course = mockCourse) {
    return mount(CourseDetail, {
      props: { course },
      global: {
        plugins: [createPinia()],
        stubs: {
          RouterLink: true,
        },
      },
    })
  }

  it('renders course name', () => {
    const wrapper = mountCourseDetail()
    expect(wrapper.text()).toContain('資料結構')
  })

  it('renders course tags', () => {
    const wrapper = mountCourseDetail()
    expect(wrapper.text()).toContain('#必修')
    expect(wrapper.text()).toContain('#程式設計')
  })

  it('limits tags to 6', () => {
    const courseWithManyTags = {
      ...mockCourse,
      tags: ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7', 'tag8'],
    }
    const wrapper = mountCourseDetail(courseWithManyTags)
    const tags = wrapper.findAll('.cdp__tag')
    expect(tags.length).toBe(6)
  })

  it('renders search bar', () => {
    const wrapper = mountCourseDetail()
    expect(wrapper.find('.cdp__search-wrapper').exists()).toBe(true)
  })

  it('renders basic info component', () => {
    const wrapper = mountCourseDetail()
    expect(wrapper.findComponent(CourseBasicInfo).exists()).toBe(true)
  })

  it('renders star evaluation component', () => {
    const wrapper = mountCourseDetail()
    expect(wrapper.findComponent(CourseStarEvaluation).exists()).toBe(true)
  })

  it('renders AI summary component', () => {
    const wrapper = mountCourseDetail()
    expect(wrapper.findComponent(CourseAISummary).exists()).toBe(true)
  })

  it('renders comments component', () => {
    const wrapper = mountCourseDetail()
    expect(wrapper.findComponent(CourseComments).exists()).toBe(true)
  })

  it('passes empty array to comments when no comments', () => {
    const courseWithoutComments = { ...mockCourse, comments: undefined }
    const wrapper = mountCourseDetail(courseWithoutComments)
    const commentsComponent = wrapper.findComponent(CourseComments)
    expect(commentsComponent.props('comments')).toEqual([])
  })

  it('re-emits submit review from AI summary', async () => {
    const wrapper = mountCourseDetail()
    const aiSummary = wrapper.findComponent(CourseAISummary)
    aiSummary.vm.$emit('submitReview', {
      title: 't',
      content: 'c',
      ratings: { reward: 5, score: 4, easiness: 3, teacherStyle: 4 },
      weeklyHours: '5h',
      textbook: 'x',
      semester: '114-1',
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('submitReview')).toBeTruthy()
  })
})
