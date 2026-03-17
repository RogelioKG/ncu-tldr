<script setup lang="ts">
// NavBar 元件 - 磨砂玻璃效果導航列
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getDataSourceLabel } from '@/api/client'
import { useAuthStore } from '@/stores/useAuthStore'

const isDev = import.meta.env.DEV

const SCROLL_THRESHOLD_PX = 20

const isScrolled = ref(false)
const menuOpen = ref(false)
const authStore = useAuthStore()
const route = useRoute()

const navItems = computed(() => [
  { name: 'home', label: '首頁' },
  { name: 'my-reviews', label: '我的評價' },
  { name: 'my-level', label: '積分商城' },
  { name: 'about', label: '關於我們' },
])

watch(() => route?.name, () => {
  menuOpen.value = false
})

watch(menuOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

let ticking = false
function handleScroll() {
  if (!ticking) {
    requestAnimationFrame(() => {
      isScrolled.value = window.scrollY > SCROLL_THRESHOLD_PX
      ticking = false
    })
    ticking = true
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

function handleLogout() {
  authStore.logout()
}

function closeMenu() {
  menuOpen.value = false
}
</script>

<template>
  <nav class="navbar" :class="{ 'navbar--scrolled': isScrolled }">
    <div class="navbar__container">
      <button
        type="button"
        class="navbar__menu-btn"
        aria-label="開啟選單"
        :aria-expanded="menuOpen"
        @click="menuOpen = !menuOpen"
      >
        <span class="navbar__menu-icon" />
      </button>
      <div class="navbar__brand-wrap">
        <RouterLink to="/" class="navbar__brand" @click="closeMenu">
          <img src="/logo.png" alt="NCU TLDR Logo" class="navbar__logo" width="33" height="38">
          <span class="navbar__title">NCU TLDR</span>
        </RouterLink>
        <span
          v-if="isDev"
          class="navbar__data-source"
          :title="`資料來源：${getDataSourceLabel() === 'API' ? '後端 API / DB' : '前端 Mock'}`"
        >
          資料: {{ getDataSourceLabel() }}
        </span>
      </div>
      <div class="navbar__links" role="navigation" aria-label="主要導覽">
        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          :to="{ name: item.name }"
          class="navbar__link"
          active-class="navbar__link--active"
        >
          {{ item.label }}
        </RouterLink>
      </div>
      <div class="navbar__actions">
        <template v-if="authStore.isLoggedIn">
          <span class="navbar__user">{{ authStore.displayName }}</span>
          <button type="button" class="navbar__btn navbar__btn--ghost" @click="handleLogout">
            登出
          </button>
        </template>
        <template v-else>
          <RouterLink :to="{ name: 'login' }" class="navbar__btn navbar__btn--ghost">
            登入
          </RouterLink>
          <RouterLink :to="{ name: 'register' }" class="navbar__btn navbar__btn--primary">
            註冊
          </RouterLink>
        </template>
      </div>
    </div>
    <Teleport to="body">
      <Transition name="navbar-overlay">
        <button
          v-if="menuOpen"
          type="button"
          class="navbar__overlay"
          aria-label="關閉選單"
          tabindex="-1"
          @click="closeMenu"
        />
      </Transition>
      <Transition name="navbar-drawer">
        <aside
          v-if="menuOpen"
          class="navbar__drawer"
          role="dialog"
          aria-label="主要導覽選單"
          aria-modal="true"
        >
          <nav class="navbar__drawer-nav" role="navigation" aria-label="主要導覽">
            <RouterLink
              v-for="item in navItems"
              :key="item.name"
              :to="{ name: item.name }"
              class="navbar__drawer-link"
              :class="{ 'navbar__drawer-link--active': route?.name === item.name }"
              @click="closeMenu"
            >
              {{ item.label }}
            </RouterLink>
          </nav>
        </aside>
      </Transition>
    </Teleport>
  </nav>
</template>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  transition: all var(--transition-normal);
}

.navbar--scrolled {
  padding: var(--spacing-sm) var(--spacing-xl);
  box-shadow: var(--shadow-md);
  background: var(--glass-bg-scrolled);
}

.navbar__container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar__brand-wrap {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.navbar__brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  text-decoration: none;
}

.navbar__data-source {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  background: var(--color-background-alt);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.navbar__logo {
  object-fit: contain;
}

.navbar__title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: 0.5px;
}

.navbar__links {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}

.navbar__link {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  padding: var(--spacing-sm) 0;
  position: relative;
  transition: color var(--transition-fast);
  text-decoration: none;
}

.navbar__link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--color-accent-primary);
  border-radius: var(--radius-full);
  transition: width var(--transition-normal);
}

.navbar__link:hover,
.navbar__link--active {
  color: var(--color-text-primary);
}

.navbar__link:hover::after,
.navbar__link--active::after {
  width: 100%;
}

.navbar__actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.navbar__user {
  font-size: var(--font-size-sm);
  font-weight: 600;
}

.navbar__btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
}

.navbar__btn--ghost {
  color: var(--color-text-secondary);
  background: transparent;
}

.navbar__btn--ghost:hover {
  color: var(--color-text-primary);
  background: var(--color-background-alt);
}

.navbar__btn--primary {
  color: white;
  background: var(--color-accent-primary);
}

.navbar__btn--primary:hover {
  background: var(--color-text-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* 漢堡選單按鈕：僅小螢幕顯示 */
.navbar__menu-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  margin: 0;
  margin-right: var(--spacing-sm);
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-text-primary);
  cursor: pointer;
}

.navbar__menu-icon {
  position: relative;
  width: 22px;
  height: 2px;
  background: currentColor;
  border-radius: var(--radius-full);
}

.navbar__menu-icon::before,
.navbar__menu-icon::after {
  content: '';
  position: absolute;
  left: 0;
  width: 22px;
  height: 2px;
  background: currentColor;
  border-radius: var(--radius-full);
  transition: transform var(--transition-normal);
}

.navbar__menu-icon::before {
  top: -7px;
}

.navbar__menu-icon::after {
  top: 7px;
}

/* overlay：點擊關閉，低於 drawer */
.navbar__overlay {
  position: fixed;
  inset: 0;
  z-index: 1100;
  background: rgba(0, 0, 0, 0.4);
  border: none;
  cursor: default;
}

/* drawer：左上角展開選單，高於 overlay */
.navbar__drawer {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: min(280px, 85vw);
  z-index: 1101;
  padding: calc(var(--spacing-md) + 56px) var(--spacing-lg) var(--spacing-lg);
  background: var(--glass-bg-scrolled);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: var(--shadow-lg);
}

.navbar__drawer-nav {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.navbar__drawer-link {
  display: block;
  padding: var(--spacing-md) var(--spacing-sm);
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--color-text-secondary);
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: background var(--transition-fast), color var(--transition-fast);
}

.navbar__drawer-link:hover,
.navbar__drawer-link--active {
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.1);
}

/* overlay / drawer 進出場 */
.navbar-overlay-enter-active,
.navbar-overlay-leave-active {
  transition: opacity var(--transition-normal);
}

.navbar-overlay-enter-from,
.navbar-overlay-leave-to {
  opacity: 0;
}

.navbar-drawer-enter-active,
.navbar-drawer-leave-active {
  transition: transform var(--transition-normal);
}

.navbar-drawer-enter-from,
.navbar-drawer-leave-to {
  transform: translateX(-100%);
}

/* 響應式：小螢幕隱藏連結列、顯示漢堡 */
@media (max-width: 768px) {
  .navbar__menu-btn {
    display: flex;
  }

  .navbar__links {
    display: none;
  }

  .navbar__container {
    padding: 0 var(--spacing-md);
  }
}
</style>
