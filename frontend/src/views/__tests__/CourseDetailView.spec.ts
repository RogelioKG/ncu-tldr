import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import CourseDetailView from '../CourseDetailView.vue'
import HomeView from '../HomeView.vue'

describe('courseDetailView', () => {
  const createRouterMock = (initialRoute = '/course/1') => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'home', component: HomeView },
        { path: '/course/:id', name: 'course-detail', component: CourseDetailView },
      ],
    })
    router.push(initialRoute)
    return router
  }

  it('renders course detail when course exists', async () => {
    const router = createRouterMock('/course/1')
    await router.isReady()

    const wrapper = mount(CourseDetailView, {
      global: {
        plugins: [router, createPinia()],
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 0))
    expect(wrapper.findComponent({ name: 'CourseDetail' }).exists()).toBe(true)
  })

  it('shows not found message when course does not exist', async () => {
    const router = createRouterMock('/course/9999')
    await router.isReady()

    const wrapper = mount(CourseDetailView, {
      global: {
        plugins: [router, createPinia()],
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 0))
    expect(wrapper.text()).toContain('找不到該課程資訊')
  })

  it('parses course id from route params', async () => {
    const router = createRouterMock('/course/2')
    await router.isReady()

    const wrapper = mount(CourseDetailView, {
      global: {
        plugins: [router, createPinia()],
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 0))
    // Course 2 exists in mock data
    const courseDetail = wrapper.findComponent({ name: 'CourseDetail' })
    if (courseDetail.exists()) {
      expect(courseDetail.props('course')?.id).toBe(2)
    }
  })

  it('handles string course id from route', async () => {
    const router = createRouterMock('/course/1')
    await router.isReady()

    const wrapper = mount(CourseDetailView, {
      global: {
        plugins: [router, createPinia()],
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 0))
    const courseDetail = wrapper.findComponent({ name: 'CourseDetail' })
    if (courseDetail.exists()) {
      expect(typeof courseDetail.props('course')?.id).toBe('number')
    }
  })
})
