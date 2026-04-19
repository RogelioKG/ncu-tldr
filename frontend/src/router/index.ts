import type { RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'
import CourseDetailView from '../views/CourseDetailView.vue'
import HomeView from '../views/HomeView.vue'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true },
  },
  {
    path: '/course/:id',
    name: 'course-detail',
    component: CourseDetailView,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
  },
  {
    path: '/my-reviews',
    name: 'my-reviews',
    component: () => import('../views/MyReviewsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/my-level',
    name: 'my-level',
    component: () => import('../views/PointsShopView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutView.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition)
      return savedPosition
    else
      return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth)
    return true

  const { useAuthStore } = await import('@/stores/useAuthStore')
  const auth = useAuthStore()

  if (!auth.isLoggedIn)
    return { name: 'login', query: { redirect: to.fullPath } }

  return true
})

export default router
