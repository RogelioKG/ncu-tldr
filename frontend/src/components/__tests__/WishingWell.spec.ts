import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'
import { nextTick } from 'vue'
import WishingWell from '../WishingWell.vue'
import WishingWellFormToast from '../WishingWellFormToast.vue'

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

  it('renders course names and teachers', async () => {
    const wrapper = await mountWishingWell()
    const items = wrapper.findAll('.wishing-well__item')
    items.forEach((item) => {
      expect(item.find('.wishing-well__course-name').exists()).toBe(true)
      expect(item.find('.wishing-well__teacher').exists()).toBe(true)
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

  it('adds a new wish item after toast form submit', async () => {
    const wrapper = await mountWishingWell()
    const originalItemCount = wrapper.findAll('.wishing-well__item').length

    await wrapper.get('.wishing-well__add-btn').trigger('click')
    wrapper.getComponent(WishingWellFormToast).vm.$emit('submit', {
      name: '雲端原生應用',
      teacher: '王小明',
    })
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 0))

    const items = wrapper.findAll('.wishing-well__item')
    expect(items.length).toBe(originalItemCount + 1)
    expect(wrapper.text()).toContain('雲端原生應用')
    expect(wrapper.text()).toContain('王小明')
  })

  it('renders background cards for stacking effect', async () => {
    const wrapper = await mountWishingWell()
    expect(wrapper.find('.wishing-well__bg-card--1').exists()).toBe(true)
    expect(wrapper.find('.wishing-well__bg-card--2').exists()).toBe(true)
  })
})
