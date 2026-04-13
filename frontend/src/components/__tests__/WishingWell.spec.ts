import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'
import { mockWishList } from '@/mock/wishList'
import { useWishStore } from '@/stores/useWishStore'
import WishingWell from '../WishingWell.vue'
import WishingWellFormToast from '../WishingWellFormToast.vue'

vi.mock('@/api/wishlist', async (importOriginal) => {
  const mod = await importOriginal() as typeof import('@/api/wishlist')
  return {
    ...mod,
    getWishlist: vi.fn().mockResolvedValue(mockWishList),
    voteForCourse: vi.fn().mockResolvedValue(undefined),
  }
})

describe('wishingWell', () => {
  async function mountWishingWell() {
    const wrapper = mount(WishingWell, {
      global: {
        plugins: [createPinia()],
      },
    })
    await nextTick()
    return wrapper
  }

  it('renders title', async () => {
    const wrapper = await mountWishingWell()
    expect(wrapper.text()).toContain('許願池')
  })

  it('renders wish list items', async () => {
    const wrapper = await mountWishingWell()
    const items = wrapper.findAll('.wishing-well__item')
    expect(items.length).toBeGreaterThan(0)
  })

  it('renders course titles and vote counts', async () => {
    const wrapper = await mountWishingWell()
    const items = wrapper.findAll('.wishing-well__item')
    items.forEach((item) => {
      expect(item.find('.wishing-well__course-name').exists()).toBe(true)
      expect(item.find('.wishing-well__votes').exists()).toBe(true)
    })
  })

  it('renders item numbers', async () => {
    const wrapper = await mountWishingWell()
    const numbers = wrapper.findAll('.wishing-well__number')
    numbers.forEach((num, idx) => {
      expect(num.text()).toBe(`${idx + 1}.`)
    })
  })

  it('applies hover class on mouseenter', async () => {
    const wrapper = await mountWishingWell()
    const firstItem = wrapper.find('.wishing-well__item')
    await firstItem.trigger('mouseenter')
    expect(firstItem.classes()).toContain('wishing-well__item--hovered')
  })

  it('removes hover class on mouseleave', async () => {
    const wrapper = await mountWishingWell()
    const firstItem = wrapper.find('.wishing-well__item')
    await firstItem.trigger('mouseenter')
    await firstItem.trigger('mouseleave')
    expect(firstItem.classes()).not.toContain('wishing-well__item--hovered')
  })

  it('emits select-course event when item is clicked', async () => {
    const wrapper = await mountWishingWell()
    const firstItem = wrapper.find('.wishing-well__item')
    await firstItem.trigger('click')
    expect(wrapper.emitted('selectCourse')).toBeTruthy()
  })

  it('renders add button with image', async () => {
    const wrapper = await mountWishingWell()
    const addBtn = wrapper.find('.wishing-well__add-btn')
    expect(addBtn.exists()).toBe(true)
    expect(addBtn.find('img').exists()).toBe(true)
  })

  it('opens wishing well form toast when add button is clicked', async () => {
    const wrapper = await mountWishingWell()
    await wrapper.get('.wishing-well__add-btn').trigger('click')
    expect(wrapper.findComponent(WishingWellFormToast).exists()).toBe(true)
  })

  it('adds a new wish item after voting', async () => {
    const pinia = createPinia()
    const wrapper = mount(WishingWell, {
      global: {
        plugins: [pinia],
      },
    })
    await nextTick()
    await vi.waitFor(() => {
      expect(wrapper.findAll('.wishing-well__item').length).toBe(mockWishList.length)
    }, { timeout: 2000 })
    const originalItemCount = wrapper.findAll('.wishing-well__item').length

    setActivePinia(pinia)
    const wishStore = useWishStore()
    wishStore.wishes = [
      ...wishStore.wishes,
      { courseId: 999, title: '雲端原生應用', voteCount: 1, hasVoted: true },
    ]
    await nextTick()

    const items = wrapper.findAll('.wishing-well__item')
    expect(items.length).toBe(originalItemCount + 1)
    expect(wrapper.text()).toContain('雲端原生應用')
  })

  it('renders background cards for stacking effect', async () => {
    const wrapper = await mountWishingWell()
    expect(wrapper.find('.wishing-well__bg-card--1').exists()).toBe(true)
    expect(wrapper.find('.wishing-well__bg-card--2').exists()).toBe(true)
  })
})
