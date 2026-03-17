<script setup lang="ts">
const zones = [
  {
    id: 'tickets',
    title: '抽獎券 / 折價券',
    subtitle: '用積分兌換好運',
    icon: '🎫',
  },
  {
    id: 'stickers',
    title: '原創貼圖',
    subtitle: 'TLDR 限定貼圖',
    icon: '✨',
  },
  {
    id: 'fresh',
    title: '生鮮砸貨',
    subtitle: '限時搶購',
    icon: '🥬',
  },
] as const
</script>

<template>
  <div class="points-shop">
    <h1 class="points-shop__title">
      積分商城
    </h1>

    <!-- 區塊一：抽獎券／折價券 － 票券帶造型 -->
    <section
      class="points-shop__zone points-shop__zone--ticket"
      aria-labelledby="zone-tickets"
    >
      <div class="points-shop__zone-inner points-shop__zone-inner--ticket">
        <span class="points-shop__zone-icon" aria-hidden="true">
          {{ zones[0].icon }}
        </span>
        <h2 id="zone-tickets" class="points-shop__zone-title">
          {{ zones[0].title }}
        </h2>
        <p class="points-shop__zone-subtitle">
          {{ zones[0].subtitle }}
        </p>
        <p class="points-shop__zone-cta">
          敬請期待
        </p>
      </div>
    </section>

    <!-- 區塊二與三：並排 -->
    <div class="points-shop__row">
      <!-- 區塊二：原創貼圖 － 貼紙格 -->
      <section
        class="points-shop__zone points-shop__zone--sticker"
        aria-labelledby="zone-stickers"
      >
        <h2 id="zone-stickers" class="points-shop__zone-title points-shop__zone-title--sticker">
          {{ zones[1].title }}
        </h2>
        <p class="points-shop__zone-subtitle">
          {{ zones[1].subtitle }}
        </p>
        <div class="points-shop__sticker-grid">
          <div
            v-for="i in 6"
            :key="i"
            class="points-shop__sticker"
            :style="{ '--sticker-rotate': `${(i % 3) * 4 - 4}deg` }"
          >
            <span class="points-shop__sticker-emoji">{{ zones[1].icon }}</span>
            <span class="points-shop__sticker-label">敬請期待</span>
          </div>
        </div>
      </section>

      <!-- 區塊三：生鮮砸貨 － 斜切區塊 -->
      <section
        class="points-shop__zone points-shop__zone--fresh"
        aria-labelledby="zone-fresh"
      >
        <div class="points-shop__fresh-accent" />
        <div class="points-shop__zone-inner points-shop__zone-inner--fresh">
          <span class="points-shop__zone-icon" aria-hidden="true">
            {{ zones[2].icon }}
          </span>
          <h2 id="zone-fresh" class="points-shop__zone-title">
            {{ zones[2].title }}
          </h2>
          <p class="points-shop__zone-subtitle">
            {{ zones[2].subtitle }}
          </p>
          <p class="points-shop__zone-cta">
            敬請期待
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.points-shop {
  max-width: 900px;
  margin: 0 auto;
  padding: var(--spacing-xl);
}

.points-shop__title {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
  font-size: var(--font-size-2xl);
}

/* ----- 區塊一：票券帶 ----- */
.points-shop__zone--ticket {
  margin-bottom: var(--spacing-2xl);
}

.points-shop__zone-inner--ticket {
  position: relative;
  padding: var(--spacing-xl) var(--spacing-2xl);
  background: linear-gradient(135deg, #fef9e6 0%, #fef3cd 50%, #fde9a0 100%);
  border: 2px dashed var(--color-star-filled);
  border-radius: var(--radius-md);
  transform: rotate(-0.8deg);
  box-shadow: var(--shadow-md);
}

.points-shop__zone-inner--ticket::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 12px;
  height: 80%;
  background: repeating-linear-gradient(
    90deg,
    transparent,
    transparent 3px,
    var(--color-star-filled) 3px,
    var(--color-star-filled) 5px
  );
  border-radius: 0 4px 4px 0;
  opacity: 0.6;
}

.points-shop__zone-inner--ticket .points-shop__zone-icon {
  font-size: 2rem;
}

.points-shop__zone-title {
  margin: 0 0 var(--spacing-xs);
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
}

.points-shop__zone-subtitle {
  margin: 0 0 var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.points-shop__zone-cta {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  font-weight: 500;
}

/* ----- 區塊二與三並排 ----- */
.points-shop__row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);
}

@media (max-width: 640px) {
  .points-shop__row {
    grid-template-columns: 1fr;
  }
}

/* ----- 區塊二：貼紙格 ----- */
.points-shop__zone--sticker {
  padding: var(--spacing-lg);
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.points-shop__zone-title--sticker {
  margin-bottom: var(--spacing-xs);
}

.points-shop__zone--sticker .points-shop__zone-subtitle {
  margin-bottom: var(--spacing-lg);
}

.points-shop__sticker-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.points-shop__sticker {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  background: linear-gradient(145deg, #f8f6f0 0%, #efece4 100%);
  border: 2px solid var(--color-accent-secondary);
  border-radius: var(--radius-md);
  transform: rotate(var(--sticker-rotate, 0deg));
  box-shadow:
    var(--shadow-sm),
    2px 2px 0 rgba(0, 0, 0, 0.06);
  transition: transform var(--transition-fast);
}

.points-shop__sticker:hover {
  transform: rotate(var(--sticker-rotate, 0deg)) scale(1.02);
}

.points-shop__sticker-emoji {
  font-size: 1.75rem;
}

.points-shop__sticker-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

/* ----- 區塊三：生鮮砸貨斜切 ----- */
.points-shop__zone--fresh {
  position: relative;
  overflow: hidden;
  padding: 0;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.points-shop__fresh-accent {
  position: absolute;
  top: 0;
  right: 0;
  width: 45%;
  height: 100%;
  background: linear-gradient(165deg, var(--color-accent-secondary) 0%, var(--color-accent-teal) 100%);
  clip-path: polygon(30% 0, 100% 0, 100% 100%, 0 100%);
  opacity: 0.85;
}

.points-shop__zone-inner--fresh {
  position: relative;
  padding: var(--spacing-xl);
  min-height: 220px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.points-shop__zone-inner--fresh .points-shop__zone-title {
  color: var(--color-text-primary);
}

.points-shop__zone-inner--fresh .points-shop__zone-icon {
  font-size: 2.5rem;
  margin-bottom: var(--spacing-sm);
}
</style>
