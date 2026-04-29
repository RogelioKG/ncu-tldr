<script setup lang="ts">
import { useFocusTrap } from '@vueuse/integrations/useFocusTrap'
import { nextTick, onUnmounted, ref, watch } from 'vue'
import sorryDolphin from '@/assets/sorry_dophin.png'

const props = defineProps<{
  visible: boolean
  title?: string
  message?: string
}>()

const emit = defineEmits<{
  close: []
}>()

const dialogRef = ref<HTMLElement | null>(null)
const { activate, deactivate } = useFocusTrap(dialogRef, { allowOutsideClick: true })

function closeToast() {
  emit('close')
}

function safeActivateFocusTrap() {
  try {
    activate()
  }
  catch {
    // Ignore trap activation failures and keep the toast usable.
  }
}

function safeDeactivateFocusTrap() {
  try {
    deactivate()
  }
  catch {
    // Ignore trap deactivation failures and keep close flow stable.
  }
}

watch(
  () => props.visible,
  async (visible) => {
    if (visible) {
      await nextTick()
      safeActivateFocusTrap()
      return
    }

    safeDeactivateFocusTrap()
  },
  { flush: 'post' },
)

onUnmounted(() => {
  safeDeactivateFocusTrap()
})

function handleReport() {
  // TODO: 未來會通知後台管理員此功能有問題，請檢查 log
  closeToast()
}
</script>

<template>
  <Teleport to="body">
    <Transition name="error-fade">
      <div v-if="visible" class="error-overlay" @click.self="closeToast">
        <div ref="dialogRef" class="error-toast" role="alert" aria-label="錯誤訊息">
          <button
            class="error-toast__close"
            type="button"
            aria-label="關閉"
            @click="closeToast"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>

          <div class="error-toast__content">
            <div class="error-toast__image-wrapper">
              <img
                :src="sorryDolphin"
                alt="抱歉的海豚"
                class="error-toast__image"
              >
            </div>
            <div class="error-toast__text">
              <h3 class="error-toast__title">
                {{ title ?? '哎呀，出了點小狀況' }}
              </h3>
              <p class="error-toast__message">
                {{ message ?? '不好意思讓你遇到這個問題了！我們已經知道囉，管理員會盡快來處理，請稍後再試試看吧～' }}
              </p>
            </div>
          </div>

          <button
            class="error-toast__report-btn"
            type="button"
            @click="handleReport"
          >
            傳送錯誤資訊
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.error-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  padding: var(--spacing-md);
}

.error-toast {
  position: relative;
  width: 100%;
  max-width: 480px;
  border-radius: var(--radius-xl);
  background: var(--color-surface);
  box-shadow: var(--shadow-xl);
  padding: var(--spacing-lg) var(--spacing-xl);
}

.error-toast__close {
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
}

.error-toast__close:hover {
  color: var(--color-text-primary);
  background: var(--color-background-alt);
}

.error-toast__close svg {
  width: 18px;
  height: 18px;
}

.error-toast__content {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.error-toast__image-wrapper {
  flex-shrink: 0;
  width: 160px;
  height: 160px;
}

.error-toast__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  mask-image: radial-gradient(circle, black 50%, transparent 100%);
  -webkit-mask-image: radial-gradient(circle, black 50%, transparent 100%);
}

.error-toast__text {
  flex: 1;
  min-width: 0;
  padding-right: var(--spacing-lg);
}

.error-toast__title {
  font-size: var(--font-size-lg);
  font-weight: 800;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
}

.error-toast__message {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  line-height: 1.8;
  margin: 0;
}

.error-toast__report-btn {
  width: 100%;
  padding: 12px;
  border-radius: var(--radius-full);
  background: var(--color-accent-primary);
  color: white;
  font-size: var(--font-size-sm);
  font-weight: 600;
  transition: all var(--transition-fast);
}

.error-toast__report-btn:hover {
  background: var(--color-text-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.error-fade-enter-active,
.error-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.error-fade-enter-from,
.error-fade-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}

/* Tablet */
@media (max-width: 768px) {
  .error-toast {
    max-width: 400px;
  }

  .error-toast__image-wrapper {
    width: 120px;
    height: 120px;
  }
}

/* Mobile */
@media (max-width: 480px) {
  .error-toast {
    max-width: 100%;
    padding: var(--spacing-md) var(--spacing-lg);
  }

  .error-toast__content {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .error-toast__image-wrapper {
    width: 100px;
    height: 100px;
  }

  .error-toast__text {
    padding-right: 0;
  }

  .error-toast__title {
    font-size: var(--font-size-md);
  }

  .error-toast__message {
    font-size: var(--font-size-sm);
  }
}
</style>
