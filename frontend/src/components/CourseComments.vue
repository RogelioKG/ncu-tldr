<script setup lang="ts">
import type { CommentTreeNode, CourseComment } from '@/types'
import { computed, ref } from 'vue'
import { buildCommentTree, flattenDescendants } from '@/types'

const props = defineProps<{
  comments: CourseComment[]
}>()

const emit = defineEmits<{
  reply: [{ parentId: number, content: string }]
  deleteComment: [{ commentId: number }]
  submitComment: [{ content: string }]
}>()

interface RenderGroup {
  root: CommentTreeNode
  descendants: CommentTreeNode[]
}

type SortMode = 'date' | 'popular'
const sortMode = ref<SortMode>('date')
const newComment = ref('')
const replyingToId = ref<number | null>(null)
const replyingToRootId = ref<number | null>(null)
const replyTargetDepth = ref(0)
const replyInput = ref('')
const expandedRoots = ref<Set<number>>(new Set())

function toggleReplies(rootId: number) {
  const collapsing = isExpanded(rootId)
  if (collapsing && replyingToRootId.value === rootId)
    cancelReply()
  const next = new Set(expandedRoots.value)
  if (next.has(rootId))
    next.delete(rootId)
  else
    next.add(rootId)
  expandedRoots.value = next
}

function isExpanded(rootId: number): boolean {
  return expandedRoots.value.has(rootId)
}

function sortByDate(a: CourseComment, b: CourseComment) {
  return b.date.localeCompare(a.date)
}
function sortByPopular(a: CourseComment, b: CourseComment) {
  return (b.likes - b.dislikes) - (a.likes - a.dislikes)
}

const renderGroups = computed<RenderGroup[]>(() =>
  buildCommentTree([...props.comments], sortByDate, sortByPopular, sortMode.value)
    .map(root => ({ root, descendants: flattenDescendants(root) })),
)

function submitComment() {
  if (!newComment.value.trim())
    return
  emit('submitComment', { content: newComment.value.trim() })
  newComment.value = ''
}

function startReply(node: CommentTreeNode) {
  replyingToId.value = node.comment.id
  replyingToRootId.value = node.rootId
  replyTargetDepth.value = node.depth
  replyInput.value = ''
  if (node.depth > 0 && !isExpanded(node.rootId))
    toggleReplies(node.rootId)
}

function cancelReply() {
  replyingToId.value = null
  replyingToRootId.value = null
  replyInput.value = ''
}

function submitReply() {
  if (replyingToId.value == null || !replyInput.value.trim())
    return
  emit('reply', { parentId: replyingToId.value, content: replyInput.value.trim() })
  replyingToId.value = null
  replyingToRootId.value = null
  replyInput.value = ''
}

function deleteComment(commentId: number) {
  emit('deleteComment', { commentId })
}

function displayUserLabel(comment: CourseComment): string {
  return comment.title ? `${comment.user}：${comment.title}` : comment.user
}

function formatDate(isoString: string): string {
  const d = new Date(isoString)
  if (Number.isNaN(d.getTime()))
    return isoString
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${mm}/${dd} ${hh}:${min}`
}
</script>

<template>
  <section class="comments" aria-label="匿名留言串">
    <header class="comments__header">
      <h2 class="comments__title">
        匿名留言串
      </h2>
      <div class="comments__sort">
        <span class="comments__sort-label">排序：</span>
        <button
          type="button"
          class="comments__sort-btn"
          :class="{ 'comments__sort-btn--active': sortMode === 'date' }"
          @click="sortMode = 'date'"
        >
          日期
        </button>
        <button
          type="button"
          class="comments__sort-btn"
          :class="{ 'comments__sort-btn--active': sortMode === 'popular' }"
          @click="sortMode = 'popular'"
        >
          熱門度
        </button>
      </div>
    </header>

    <!-- 留言列表（樹狀） -->
    <ul v-if="renderGroups.length" class="comments__list">
      <template v-for="group in renderGroups" :key="group.root.comment.id">
        <!-- 根留言 -->
        <li class="comments__item">
          <div class="comments__item-top">
            <div class="comments__user-row">
              <span class="comments__avatar">👤</span>
              <span class="comments__user">{{ displayUserLabel(group.root.comment) }}</span>
            </div>
            <span class="comments__date">({{ formatDate(group.root.comment.date) }})</span>
          </div>
          <p class="comments__content">
            {{ group.root.comment.content }}
          </p>
          <div v-if="!group.root.comment.isDeleted" class="comments__actions">
            <button type="button" class="comments__vote-btn" aria-label="按讚" disabled title="即將推出">
              👍 <span v-if="group.root.comment.likes">{{ group.root.comment.likes }}</span>
            </button>
            <button type="button" class="comments__vote-btn" aria-label="倒讚" disabled title="即將推出">
              👎 <span v-if="group.root.comment.dislikes">{{ group.root.comment.dislikes }}</span>
            </button>
            <button
              type="button"
              class="comments__reply-btn"
              aria-label="回覆"
              @click="startReply(group.root)"
            >
              回覆
            </button>
            <button
              v-if="group.root.comment.canDelete"
              type="button"
              class="comments__delete-btn"
              aria-label="刪除留言"
              @click="deleteComment(group.root.comment.id)"
            >
              刪除
            </button>
          </div>
          <button
            v-if="group.descendants.length > 0"
            type="button"
            class="comments__toggle-replies-btn"
            @click="toggleReplies(group.root.comment.id)"
          >
            {{ isExpanded(group.root.comment.id) ? '收起所有回覆' : `展開所有回覆（${group.descendants.length}）` }}
          </button>
        </li>
        <!-- 回覆根留言的輸入框（緊接於根留言下方） -->
        <li
          v-if="replyingToId === group.root.comment.id"
          class="comments__reply-form"
          :style="{ '--depth': 1 }"
        >
          <input
            :ref="(el) => { if (el) (el as HTMLInputElement).focus() }"
            v-model="replyInput"
            type="text"
            class="comments__input"
            placeholder="回覆此留言..."
            @keydown.enter="submitReply"
            @keydown.esc="cancelReply"
          >
          <div class="comments__reply-actions">
            <button
              type="button"
              class="comments__submit-btn"
              :disabled="!replyInput.trim()"
              @click="submitReply"
            >
              發布
            </button>
            <button
              type="button"
              class="comments__cancel-btn"
              @click="cancelReply"
            >
              取消
            </button>
          </div>
        </li>
        <!-- 所有子孫留言（深度 >= 1），每則後緊接其回覆輸入框 -->
        <template v-for="node in group.descendants" :key="node.comment.id">
          <li
            v-show="isExpanded(group.root.comment.id)"
            class="comments__item comments__item--reply"
            :style="{ '--depth': node.depth }"
          >
            <div class="comments__item-top">
              <div class="comments__user-row">
                <span class="comments__avatar">👤</span>
                <span class="comments__user">{{ displayUserLabel(node.comment) }}</span>
              </div>
              <span class="comments__date">({{ formatDate(node.comment.date) }})</span>
            </div>
            <p class="comments__content">
              {{ node.comment.content }}
            </p>
            <div v-if="!node.comment.isDeleted" class="comments__actions">
              <button type="button" class="comments__vote-btn" aria-label="按讚">
                👍 <span v-if="node.comment.likes">{{ node.comment.likes }}</span>
              </button>
              <button type="button" class="comments__vote-btn" aria-label="倒讚">
                👎 <span v-if="node.comment.dislikes">{{ node.comment.dislikes }}</span>
              </button>
              <button
                type="button"
                class="comments__reply-btn"
                aria-label="回覆"
                @click="startReply(node)"
              >
                回覆
              </button>
              <button
                v-if="node.comment.canDelete"
                type="button"
                class="comments__delete-btn"
                aria-label="刪除留言"
                @click="deleteComment(node.comment.id)"
              >
                刪除
              </button>
            </div>
          </li>
          <!-- 回覆此子孫留言的輸入框（緊接於該留言下方） -->
          <li
            v-if="replyingToId === node.comment.id"
            class="comments__reply-form"
            :style="{ '--depth': node.depth + 1 }"
          >
            <input
              :ref="(el) => { if (el) (el as HTMLInputElement).focus() }"
              v-model="replyInput"
              type="text"
              class="comments__input"
              placeholder="回覆此留言..."
              @keydown.enter="submitReply"
              @keydown.esc="cancelReply"
            >
            <div class="comments__reply-actions">
              <button
                type="button"
                class="comments__submit-btn"
                :disabled="!replyInput.trim()"
                @click="submitReply"
              >
                發布
              </button>
              <button
                type="button"
                class="comments__cancel-btn"
                @click="cancelReply"
              >
                取消
              </button>
            </div>
          </li>
        </template>
      </template>
    </ul>

    <!-- 無留言 -->
    <p v-else class="comments__empty">
      目前尚無留言，成為第一個分享心得的人吧！
    </p>

    <!-- 根留言輸入框 -->
    <div class="comments__input-row">
      <input
        v-model="newComment"
        type="text"
        class="comments__input"
        placeholder="留下您的修課心得..."
        @keydown.enter="submitComment"
      >
      <button
        type="button"
        class="comments__submit-btn"
        :disabled="!newComment.trim()"
        @click="submitComment"
      >
        發布
      </button>
    </div>
  </section>
</template>

<style scoped>
.comments {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-radius: var(--radius-xl);
  background:
    radial-gradient(circle at 5% 90%, rgba(203, 239, 242, 0.2), transparent 35%),
    rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  box-shadow: var(--shadow-md);
}

.comments__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-lg);
}

.comments__title {
  font-size: var(--font-size-xl);
  font-weight: 800;
  color: var(--color-text-primary);
}

.comments__sort {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.comments__sort-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.comments__sort-btn {
  padding: 4px 14px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  background: var(--color-background-alt);
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}

.comments__sort-btn--active {
  background: var(--color-accent-primary);
  color: white;
}

.comments__sort-btn:hover:not(.comments__sort-btn--active) {
  border-color: var(--color-accent-primary);
  color: var(--color-accent-primary);
}

.comments__list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.comments__item {
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-lg);
  background:
    linear-gradient(135deg, rgba(240, 248, 248, 0.7), rgba(255, 255, 255, 0.9));
  box-shadow: var(--shadow-sm);
}

.comments__item--reply {
  margin-left: calc(2rem * var(--depth, 1));
}

.comments__reply-form {
  margin-left: calc(2rem * var(--depth, 1));
  padding: var(--spacing-sm);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.comments__reply-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.comments__cancel-btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  background: var(--color-background-alt);
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}

.comments__cancel-btn:hover {
  border-color: var(--color-text-muted);
}

.comments__item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-xs);
}

.comments__user-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.comments__avatar {
  font-size: var(--font-size-lg);
}

.comments__user {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.comments__date {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  white-space: nowrap;
}

.comments__content {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.6;
  padding-left: 36px;
}

.comments__actions {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: flex-end;
  margin-top: var(--spacing-xs);
}

.comments__vote-btn,
.comments__reply-btn,
.comments__delete-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  background: var(--color-background-alt);
  transition: all var(--transition-fast);
}

.comments__vote-btn:hover,
.comments__reply-btn:hover,
.comments__delete-btn:hover {
  background: var(--color-accent-primary);
  color: white;
}

.comments__toggle-replies-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: var(--spacing-xs);
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  color: var(--color-accent-primary);
  background: transparent;
  border: 1px solid var(--color-accent-primary);
  transition: all var(--transition-fast);
}

.comments__toggle-replies-btn:hover {
  background: var(--color-accent-primary);
  color: white;
}

.comments__empty {
  text-align: center;
  padding: var(--spacing-xl) 0;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

/* 輸入區 */
.comments__input-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

.comments__input {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  box-shadow: var(--shadow-sm), inset 0 1px 2px rgba(0, 0, 0, 0.03);
  border: 1px solid transparent;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  transition: border-color var(--transition-fast);
}

.comments__input:focus {
  border-color: var(--color-accent-primary);
  box-shadow: var(--shadow-sm), 0 0 0 3px rgba(127, 169, 184, 0.15);
}

.comments__input::placeholder {
  color: var(--color-text-muted);
}

.comments__submit-btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-full);
  background: var(--color-accent-primary);
  color: white;
  font-weight: 600;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.comments__submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.comments__submit-btn:not(:disabled):hover {
  background: var(--color-text-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

@media (max-width: 600px) {
  .comments__header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }

  .comments__content {
    padding-left: 0;
  }

  .comments__item-top {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
