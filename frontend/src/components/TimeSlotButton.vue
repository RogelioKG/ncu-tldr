<script setup lang="ts">
defineProps<{ hasActive?: boolean }>()
const emit = defineEmits<{ open: [] }>()
</script>

<template>
  <button
    type="button"
    class="ts-btn"
    :class="{ 'ts-btn--active': hasActive }"
    :aria-label="hasActive ? '依時段查詢（已篩選）' : '依時段查詢'"
    @click="emit('open')"
  >
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
      <rect x="7" y="14" width="3" height="3" rx="0.5" fill="currentColor" stroke="none" />
    </svg>
    <span class="ts-btn__label">依時段查詢</span>
    <span v-if="hasActive" class="ts-btn__dot" aria-hidden="true" />
  </button>
</template>

<style scoped>
.ts-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  border: 1px solid transparent;
  box-shadow: var(--shadow-sm), inset 0 1px 2px rgba(0, 0, 0, 0.03);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-normal);
  overflow: hidden;
  white-space: nowrap;
  flex-shrink: 0;
}

.ts-btn__label {
  max-width: 0;
  opacity: 0;
  overflow: hidden;
  transition:
    max-width var(--transition-normal),
    opacity var(--transition-fast),
    padding-right var(--transition-normal);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.ts-btn:hover {
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
  padding: var(--spacing-sm) var(--spacing-md);
  box-shadow: var(--shadow-md), 0 0 0 3px rgba(127, 169, 184, 0.15);
}

.ts-btn:hover .ts-btn__label {
  max-width: 120px;
  opacity: 1;
}

.ts-btn--active {
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
  background: rgba(127, 169, 184, 0.08);
  padding: var(--spacing-sm) var(--spacing-md);
}

.ts-btn--active .ts-btn__label {
  max-width: 120px;
  opacity: 1;
}

.ts-btn__dot {
  width: 6px;
  height: 6px;
  border-radius: var(--radius-full);
  background: var(--color-accent-primary);
  flex-shrink: 0;
}
</style>
