import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/useAuthStore'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

const auth = useAuthStore()
auth.hydrateFromStorage().finally(() => {
  app.use(router)
  app.mount('#app')
})
