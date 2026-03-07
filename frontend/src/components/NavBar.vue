<script setup lang="ts">
// NavBar 元件 - 磨砂玻璃效果導航列
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'

// 滾動偵測門檻值 (px)
const SCROLL_THRESHOLD_PX = 20

const isScrolled = ref(false)
const authStore = useAuthStore()
const navItems = computed(() => [
  { name: 'home', label: '首頁' },
  { name: 'my-reviews', label: '我的評價' },
  { name: 'my-level', label: '我的等級' },
  { name: 'about', label: '關於我們' },
])

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
</script>

<template>
  <nav class="navbar" :class="{ 'navbar--scrolled': isScrolled }">
    <div class="navbar__container">
      <RouterLink to="/" class="navbar__brand">
        <img src="/logo.png" alt="NCU TLDR Logo" class="navbar__logo" width="33" height="38">
        <span class="navbar__title">NCU TLDR</span>
      </RouterLink>
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

.navbar__brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  text-decoration: none; /* Remove underline from link */
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

/* 響應式設計 */
@media (max-width: 768px) {
  .navbar__links {
    display: none;
  }

  .navbar__container {
    padding: 0 var(--spacing-md);
  }
}
</style>
