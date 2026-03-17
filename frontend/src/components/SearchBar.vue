<script setup lang="ts">
// SearchBar 元件 - 膠囊型搜尋欄
import { ref } from 'vue'

const emit = defineEmits<{
  search: [query: string]
}>()
const searchQuery = ref('')
const isFocused = ref(false)

function handleSearch() {
  const query = searchQuery.value.trim()
  if (query) {
    emit('search', query)
  }
}

function handleClear() {
  searchQuery.value = ''
  emit('search', '')
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') {
    handleSearch()
  }
}
</script>

<template>
  <div class="search-bar" :class="{ 'search-bar--focused': isFocused }">
    <div class="search-bar__icon">
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.3-4.3" />
      </svg>
    </div>
    <input
      v-model="searchQuery"
      type="text"
      class="search-bar__input"
      placeholder="搜尋課程、教師、關鍵字..."
      @focus="isFocused = true"
      @blur="isFocused = false"
      @keydown="handleKeydown"
    >
    <button
      v-if="searchQuery"
      type="button"
      class="search-bar__clear"
      aria-label="清除搜尋內容"
      @click="handleClear"
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
      >
        <path d="M18 6 6 18" />
        <path d="m6 6 12 12" />
      </svg>
    </button>
  </div>
</template>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-surface);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-sm), inset 0 1px 2px rgba(0, 0, 0, 0.03);
  border: 1px solid transparent;
  transition: all var(--transition-normal);
  max-width: 600px;
  width: 100%;
}

.search-bar--focused {
  border-color: var(--color-accent-primary);
  box-shadow: var(--shadow-md), 0 0 0 3px rgba(127, 169, 184, 0.15);
}

.search-bar__icon {
  flex-shrink: 0;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color var(--transition-fast);
}

.search-bar--focused .search-bar__icon {
  color: var(--color-accent-primary);
}

.search-bar__input {
  flex: 1;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  min-width: 0;
}

.search-bar__input::placeholder {
  color: var(--color-text-muted);
}

.search-bar__clear {
  flex-shrink: 0;
  padding: var(--spacing-xs);
  color: var(--color-text-muted);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.search-bar__clear:hover {
  color: var(--color-text-primary);
  background: var(--color-background-alt);
}
</style>
