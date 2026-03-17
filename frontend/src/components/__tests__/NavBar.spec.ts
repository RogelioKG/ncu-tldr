import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it } from 'vitest'
import NavBar from '../NavBar.vue'

describe('navBar', () => {
  function mountNavBar() {
    return mount(NavBar, {
      global: {
        plugins: [createPinia()],
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
          },
        },
      },
    })
  }

  it('renders brand title', () => {
    const wrapper = mountNavBar()
    expect(wrapper.text()).toContain('NCU TLDR')
  })

  it('renders navigation links', () => {
    const wrapper = mountNavBar()
    expect(wrapper.text()).toContain('首頁')
    expect(wrapper.text()).toContain('我的評價')
    expect(wrapper.text()).toContain('積分商城')
    expect(wrapper.text()).toContain('關於我們')
  })

  it('renders login and register buttons', () => {
    const wrapper = mountNavBar()
    expect(wrapper.text()).toContain('登入')
    expect(wrapper.text()).toContain('註冊')
  })

  it('applies scrolled class when scrolled', async () => {
    const wrapper = mountNavBar()

    // Simulate scroll
    Object.defineProperty(window, 'scrollY', { value: 50, writable: true })
    window.dispatchEvent(new Event('scroll'))

    await new Promise(resolve => setTimeout(resolve, 100))
    expect(wrapper.find('.navbar').classes()).toContain('navbar--scrolled')
  })

  it('does not apply scrolled class when not scrolled', () => {
    const wrapper = mountNavBar()
    expect(wrapper.find('.navbar').classes()).not.toContain('navbar--scrolled')
  })

  it('renders RouterLink to home', () => {
    const wrapper = mountNavBar()
    const brandLink = wrapper.find('.navbar__brand')
    expect(brandLink.exists()).toBe(true)
  })
})
