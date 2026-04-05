<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="not-found">
    <h1 class="not-found__title">
      404
    </h1>
    <p class="not-found__message">
      找不到你要的頁面
    </p>
    <button class="not-found__btn" type="button" @click="router.push({ name: 'home' })">
      回到首頁
    </button>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: var(--spacing-lg);
  text-align: center;
}

.not-found__title {
  font-size: var(--font-size-3xl);
  font-weight: 800;
  color: var(--color-text-muted);
}

.not-found__message {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

.not-found__btn {
  padding: var(--spacing-sm) var(--spacing-xl);
  border-radius: var(--radius-full);
  background: var(--color-accent-primary);
  color: white;
  font-weight: 600;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.not-found__btn:hover {
  background: var(--color-text-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
</style>
