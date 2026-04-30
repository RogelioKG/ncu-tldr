<script setup lang="ts">
import type { CourseComment } from '@/types'
import { useFocusTrap } from '@vueuse/integrations/useFocusTrap'
import { onUnmounted, ref, watch } from 'vue'
import ReviewCard from './ReviewCard.vue'

const props = defineProps<{
  visible: boolean
  reviews: CourseComment[]
  courseId: number
}>()

const emit = defineEmits<{
  close: []
}>()

const panelRef = ref<HTMLElement | null>(null)
const { activate, deactivate } = useFocusTrap(panelRef)

watch(() => props.visible, (v) => {
  if (v)
    activate()
  else
    deactivate()
}, { flush: 'post' })

onUnmounted(() => deactivate())

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape')
    emit('close')
}
</script>

<template>
  <Teleport to="body">
    <Transition name="rvp-slide">
      <div
        v-if="visible"
        class="rvp__overlay"
        aria-hidden="true"
        @click.self="emit('close')"
        @keydown="handleKeydown"
      >
        <div
          ref="panelRef"
          class="rvp__panel"
          role="dialog"
          aria-modal="true"
          aria-label="歷史評價"
        >
          <header class="rvp__header">
            <h3 class="rvp__title">
              歷史評價
            </h3>
            <button
              type="button"
              class="rvp__close"
              aria-label="關閉"
              @click="emit('close')"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path d="M18 6 6 18" />
                <path d="m6 6 12 12" />
              </svg>
            </button>
          </header>

          <div v-if="reviews.length" class="rvp__list">
            <ReviewCard
              v-for="review in reviews"
              :key="review.id"
              :review="review"
              :course-id="courseId"
            />
          </div>
          <div v-else class="rvp__empty">
            <p class="rvp__empty-text">
              尚無評價
            </p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.rvp__overlay {
  position: fixed;
  inset: 0;
  z-index: 9000;
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
}

.rvp__panel {
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  width: min(480px, 100%);
  background: var(--color-background, #fafafa);
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.rvp__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
}

.rvp__title {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-text-primary);
}

.rvp__close {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xs);
  border-radius: var(--radius-full);
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
}

.rvp__close:hover {
  background: var(--color-tag-bg);
  color: var(--color-text-primary);
}

.rvp__list {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.rvp__empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rvp__empty-text {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.rvp-slide-enter-active,
.rvp-slide-leave-active {
  transition: opacity 0.3s ease;
}

.rvp-slide-enter-active .rvp__panel,
.rvp-slide-leave-active .rvp__panel {
  transition: transform 0.3s ease;
}

.rvp-slide-enter-from,
.rvp-slide-leave-to {
  opacity: 0;
}

.rvp-slide-enter-from .rvp__panel,
.rvp-slide-leave-to .rvp__panel {
  transform: translateX(100%);
}
</style>
