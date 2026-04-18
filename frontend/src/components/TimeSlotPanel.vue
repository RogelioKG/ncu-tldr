<script setup lang="ts">
import type { TimeSlot } from '@/types'
import { useFocusTrap } from '@vueuse/integrations/useFocusTrap'
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps<{ visible: boolean, activeSlots?: TimeSlot[] }>()
const emit = defineEmits<{
  close: []
  submit: [slots: TimeSlot[]]
}>()

const DAYS = [
  { label: '一', value: 1 },
  { label: '二', value: 2 },
  { label: '三', value: 3 },
  { label: '四', value: 4 },
  { label: '五', value: 5 },
  { label: '六', value: 6 },
]

const PERIODS = [
  { label: '0', value: '0' },
  { label: '1', value: '1' },
  { label: '2', value: '2' },
  { label: '3', value: '3' },
  { label: '4', value: '4' },
  { label: 'Z', value: 'Z' },
  { label: '5', value: '5' },
  { label: '6', value: '6' },
  { label: '7', value: '7' },
  { label: '8', value: '8' },
  { label: '9', value: '9' },
  { label: 'A', value: 'A' },
  { label: 'B', value: 'B' },
  { label: 'C', value: 'C' },
]

const TIME_LABELS: Record<string, string> = {
  0: '07:00~08:50',
  1: '08:00~09:50',
  2: '09:00~10:50',
  3: '10:00~11:50',
  4: '11:00~12:50',
  Z: '12:00~13:50',
  5: '13:00~14:50',
  6: '14:00~15:50',
  7: '15:00~16:50',
  8: '16:00~17:50',
  9: '17:00~18:50',
  A: '18:00~19:50',
  B: '19:00~20:50',
  C: '20:00~20:50',
}

const dialogRef = ref<HTMLElement | null>(null)
const { activate, deactivate } = useFocusTrap(dialogRef)

onMounted(() => activate())
onUnmounted(() => deactivate())

const localSelected = ref<Set<string>>(new Set())

const hasSelection = computed(() => localSelected.value.size > 0)

function slotKey(day: number, period: string): string {
  return `${day}_${period}`
}

watch(
  () => props.visible,
  (v) => {
    if (v)
      localSelected.value = new Set(props.activeSlots?.map(s => slotKey(s.day, s.period)) ?? [])
  },
)

function isSelected(day: number, period: string): boolean {
  return localSelected.value.has(slotKey(day, period))
}

function toggleSlot(day: number, period: string): void {
  const key = slotKey(day, period)
  const next = new Set(localSelected.value)
  if (next.has(key))
    next.delete(key)
  else
    next.add(key)
  localSelected.value = next
}

function clearSelection(): void {
  localSelected.value = new Set()
}

function handleClose(): void {
  localSelected.value = new Set()
  emit('close')
}

function handleOverlayClick(e: MouseEvent): void {
  if ((e.target as HTMLElement).classList.contains('tsp__overlay'))
    handleClose()
}

function handleKeydown(e: KeyboardEvent): void {
  if (e.key === 'Escape')
    handleClose()
}

function handleSubmit(): void {
  const slots: TimeSlot[] = Array.from(localSelected.value, (key) => {
    const [dayStr, period] = key.split('_')
    return { day: Number(dayStr), period }
  })
  emit('submit', slots)
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <Transition name="tsp-fade">
      <div
        v-if="visible"
        class="tsp__overlay"
        role="dialog"
        aria-modal="true"
        aria-label="依時段查詢"
        @click="handleOverlayClick"
        @keydown="handleKeydown"
      >
        <div ref="dialogRef" class="tsp__panel">
          <div class="tsp__header">
            <h3 class="tsp__title">
              依時段查詢
            </h3>
            <button
              type="button"
              class="tsp__close"
              aria-label="關閉"
              @click="handleClose"
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
          </div>

          <div class="tsp__grid-wrapper">
            <div class="tsp__grid">
              <div class="tsp__corner" />
              <div
                v-for="day in DAYS"
                :key="day.value"
                class="tsp__day-header"
              >
                {{ day.label }}
              </div>

              <template
                v-for="p in PERIODS"
                :key="p.value"
              >
                <div class="tsp__period-label">
                  <span class="tsp__period-num">{{ p.label }}</span>
                  <span class="tsp__period-time">{{ TIME_LABELS[p.value] }}</span>
                </div>
                <button
                  v-for="day in DAYS"
                  :key="day.value"
                  type="button"
                  class="tsp__cell"
                  :class="{ 'tsp__cell--selected': isSelected(day.value, p.value) }"
                  :aria-label="`週${day.label} 第${p.label}節`"
                  :aria-pressed="isSelected(day.value, p.value)"
                  @click="toggleSlot(day.value, p.value)"
                />
              </template>
            </div>
          </div>

          <div class="tsp__footer">
            <button
              type="button"
              class="tsp__clear"
              :disabled="!hasSelection"
              @click="clearSelection"
            >
              清除
            </button>
            <button
              type="button"
              class="tsp__submit"
              :disabled="!hasSelection"
              @click="handleSubmit"
            >
              送出
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.tsp__overlay {
  position: fixed;
  inset: 0;
  z-index: 9000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  padding: var(--spacing-md);
}

.tsp__panel {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  padding: var(--spacing-lg);
  width: 100%;
  max-width: 580px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tsp__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
  flex-shrink: 0;
}

.tsp__title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.tsp__close {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xs);
  border-radius: var(--radius-full);
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
}

.tsp__close:hover {
  color: var(--color-text-primary);
  background: var(--color-background-alt);
}

.tsp__grid-wrapper {
  overflow-y: auto;
  flex: 1;
  margin: 0 calc(-1 * var(--spacing-xs));
  padding: 0 var(--spacing-xs);
}

.tsp__grid {
  display: grid;
  grid-template-columns: 128px repeat(6, 1fr);
  gap: 3px;
}

.tsp__corner {
  grid-column: 1;
}

.tsp__day-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xs) 0;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
}

.tsp__period-label {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 var(--spacing-xs);
  gap: 2px;
}

.tsp__period-num {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  line-height: 1;
}

.tsp__period-time {
  font-size: 10px;
  color: var(--color-text-muted);
  line-height: 1;
}

.tsp__cell {
  height: 34px;
  border-radius: var(--radius-sm);
  background: var(--color-background-alt);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tsp__cell:hover {
  border-color: var(--color-accent-primary);
  background: rgba(127, 169, 184, 0.12);
}

.tsp__cell--selected {
  background: var(--color-accent-primary);
  border-color: var(--color-accent-primary);
}

.tsp__cell--selected:hover {
  background: var(--color-accent-secondary);
  border-color: var(--color-accent-secondary);
}

.tsp__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-md);
  flex-shrink: 0;
  border-top: 1px solid var(--color-background-alt);
  margin-top: var(--spacing-md);
}

.tsp__clear {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-background-alt);
  transition: all var(--transition-fast);
}

.tsp__clear:hover:not(:disabled) {
  border-color: var(--color-text-muted);
  color: var(--color-text-primary);
}

.tsp__clear:disabled,
.tsp__submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.tsp__submit {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: 600;
  background: var(--color-accent-primary);
  color: #fff;
  border: 1px solid var(--color-accent-primary);
  transition: all var(--transition-fast);
}

.tsp__submit:hover:not(:disabled) {
  background: var(--color-accent-secondary);
  border-color: var(--color-accent-secondary);
}

.tsp-fade-enter-active,
.tsp-fade-leave-active {
  transition: opacity 0.25s ease;
}

.tsp-fade-enter-active .tsp__panel,
.tsp-fade-leave-active .tsp__panel {
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.tsp-fade-enter-from,
.tsp-fade-leave-to {
  opacity: 0;
}

.tsp-fade-enter-from .tsp__panel,
.tsp-fade-leave-to .tsp__panel {
  transform: scale(0.97);
  opacity: 0;
}
</style>
