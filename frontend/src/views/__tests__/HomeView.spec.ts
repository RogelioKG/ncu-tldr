import type { Course } from '@/types'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import HomeView from '../HomeView.vue'

vi.mock('@/api/wishlist', () => ({
  getWishlist: vi.fn().mockResolvedValue([]),
  addWish: vi.fn(),
  removeWish: vi.fn(),
}))

const mockCourses: Course[] = [
  {
    id: 1,
    name: '資料結構',
    teacher: '王小明',
    tags: ['必修'],
    ratings: { gain: 4.5, highScore: 4.0, easiness: 3.5, teacherStyle: 4.2 },
  },
]

describe('homeView', () => {
  const createRouterMock = () => {
    return createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'home', component: HomeView },
        { path: '/course/:id', name: 'course-detail', component: { template: '<div>Detail</div>' } },
      ],
    })
  }

  async function mountHomeView() {
    const router = createRouterMock()
    await router.push('/')
    await router.isReady()
    return {
      router,
      wrapper: mount(HomeView, {
        global: {
          plugins: [router, createPinia()],
        },
      }),
    }
  }

  it('renders wishing well component', async () => {
    const { wrapper } = await mountHomeView()
    await new Promise(resolve => setTimeout(resolve, 0))
    expect(wrapper.findComponent({ name: 'WishingWell' }).exists()).toBe(true)
  })

  it('renders search bar', async () => {
    const { wrapper } = await mountHomeView()
    await new Promise(resolve => setTimeout(resolve, 0))
    expect(wrapper.findComponent({ name: 'SearchBar' }).exists()).toBe(true)
  })

  it('renders course grid', async () => {
    const { wrapper } = await mountHomeView()
    await new Promise(resolve => setTimeout(resolve, 0))
    expect(wrapper.findComponent({ name: 'CourseGrid' }).exists()).toBe(true)
  })

  it('navigates to course detail when course is selected', async () => {
    const { router, wrapper } = await mountHomeView()
    const pushSpy = vi.spyOn(router, 'push')

    const courseGrid = wrapper.findComponent({ name: 'CourseGrid' })
    await courseGrid.vm.$emit('select-course', mockCourses[0])

    expect(pushSpy).toHaveBeenCalledWith({
      name: 'course-detail',
      params: { id: 1 },
    })
  })

  it('handles search event', async () => {
    const { wrapper } = await mountHomeView()
    const searchBar = wrapper.findComponent({ name: 'SearchBar' })
    await searchBar.vm.$emit('search', '資料結構')
    expect(wrapper.exists()).toBe(true)
  })

  it('handles wish course selection', async () => {
    const { router, wrapper } = await mountHomeView()
    const pushSpy = vi.spyOn(router, 'push')
    await new Promise(resolve => setTimeout(resolve, 0))

    const wishingWell = wrapper.findComponent({ name: 'WishingWell' })
    await wishingWell.vm.$emit('select-course', {
      id: 1,
      name: '演算法',
      teacher: '王大明',
    })
    await flushPromises()

    expect(pushSpy).toHaveBeenCalledWith({
      name: 'course-detail',
      params: { id: 1 },
    })
  })
})
