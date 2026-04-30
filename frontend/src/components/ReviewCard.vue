<script setup lang="ts">
import type { CourseComment } from '@/types'
import { computed, ref } from 'vue'
import { reactToReview } from '@/api/likes'

const props = defineProps<{
  review: CourseComment
  courseId?: number
  showDelete?: boolean
}>()

const emit = defineEmits<{
  delete: [{ reviewId: number }]
}>()

interface VoteState {
  likes: number
  dislikes: number
  userReaction: 'like' | 'dislike' | null
}

const localVote = ref<VoteState>({
  likes: props.review.likes,
  dislikes: props.review.dislikes,
  userReaction: props.review.userReaction ?? null,
})

async function reactReview(reaction: 'like' | 'dislike') {
  if (props.courseId === undefined)
    return
  const current = { ...localVote.value }
  const optimistic: VoteState = { ...current }

  if (current.userReaction === reaction) {
    if (reaction === 'like')
      optimistic.likes = Math.max(0, optimistic.likes - 1)
    else
      optimistic.dislikes = Math.max(0, optimistic.dislikes - 1)
    optimistic.userReaction = null
  }
  else {
    if (current.userReaction === 'like')
      optimistic.likes = Math.max(0, optimistic.likes - 1)
    else if (current.userReaction === 'dislike')
      optimistic.dislikes = Math.max(0, optimistic.dislikes - 1)
    if (reaction === 'like')
      optimistic.likes += 1
    else
      optimistic.dislikes += 1
    optimistic.userReaction = reaction
  }

  localVote.value = optimistic

  try {
    const result = await reactToReview(props.courseId, props.review.id, reaction)
    localVote.value = { ...result, userReaction: result.userReaction }
  }
  catch {
    localVote.value = current
  }
}

const ratingEntries = computed(() => {
  if (!props.review.ratings)
    return []
  const r = props.review.ratings
  return [
    { label: '收穫', value: r.gain },
    { label: '分數', value: r.highScore },
    { label: '輕鬆', value: r.easiness },
    { label: '風格', value: r.teacherStyle },
  ]
})

const formattedDate = computed(() => {
  const d = new Date(props.review.date)
  if (Number.isNaN(d.getTime()))
    return props.review.date
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}/${mm}/${dd}`
})
</script>

<template>
  <article class="rc">
    <div class="rc__header">
      <h4 class="rc__title">
        {{ review.title }}
      </h4>
      <span class="rc__date">{{ formattedDate }}</span>
    </div>
    <div v-if="ratingEntries.length" class="rc__ratings">
      <span
        v-for="entry in ratingEntries"
        :key="entry.label"
        class="rc__rating-badge"
      >
        ★ {{ entry.label }} {{ entry.value }}
      </span>
    </div>
    <p v-if="review.content" class="rc__content">
      {{ review.content }}
    </p>
    <div class="rc__footer">
      <div class="rc__votes">
        <template v-if="courseId !== undefined">
          <button
            type="button"
            class="rc__vote-btn"
            :class="{ 'rc__vote-btn--active': localVote.userReaction === 'like' }"
            aria-label="按讚"
            @click="reactReview('like')"
          >
            👍 <span v-if="localVote.likes">{{ localVote.likes }}</span>
          </button>
          <button
            type="button"
            class="rc__vote-btn"
            :class="{ 'rc__vote-btn--active': localVote.userReaction === 'dislike' }"
            aria-label="倒讚"
            @click="reactReview('dislike')"
          >
            👎 <span v-if="localVote.dislikes">{{ localVote.dislikes }}</span>
          </button>
        </template>
      </div>
      <button
        v-if="showDelete"
        type="button"
        class="rc__delete-btn"
        @click="emit('delete', { reviewId: review.id })"
      >
        刪除評價
      </button>
    </div>
  </article>
</template>

<style scoped>
.rc {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.rc__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.rc__title {
  font-weight: 700;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  flex: 1;
}

.rc__date {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  white-space: nowrap;
  flex-shrink: 0;
}

.rc__ratings {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
}

.rc__rating-badge {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  background: rgba(212, 165, 116, 0.12);
  color: var(--color-star-filled);
  font-size: var(--font-size-xs);
  font-weight: 500;
}

.rc__content {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  line-height: 1.65;
  margin-bottom: var(--spacing-sm);
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rc__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-sm);
}

.rc__votes {
  display: flex;
  gap: var(--spacing-xs);
}

.rc__vote-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  background: var(--color-tag-bg);
  transition: all var(--transition-fast);
}

.rc__vote-btn:hover {
  background: rgba(127, 169, 184, 0.12);
  color: var(--color-accent-primary);
}

.rc__vote-btn--active {
  background: rgba(127, 169, 184, 0.18);
  color: var(--color-accent-primary);
}

.rc__delete-btn {
  padding: 4px 12px;
  border-radius: var(--radius-sm);
  background: var(--color-tag-bg);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
  transition: var(--transition-fast);
}

.rc__delete-btn:hover {
  background: #ffe8e8;
  color: #b02222;
}
</style>
