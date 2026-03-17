<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import StarRatingInput from './StarRatingInput.vue'

defineProps<{
  courseName: string
}>()

const emit = defineEmits<{
  close: []
  submit: [
    payload: {
      title: string
      content: string
      ratings: {
        reward: number
        score: number
        easiness: number
        teacherStyle: number
      }
      weeklyHours: string
      textbook: string
      semester: string
    },
  ]
}>()

const form = reactive({
  semester: '',
  reward: 0,
  score: 0,
  easiness: 0,
  teacherStyle: 0,
  weeklyHours: 5,
  textbook: '',
  comment: '',
})

const weeklyHoursTouched = ref(false)
const submitted = ref(false)
const semesterOptions = computed(() => {
  const startAcademicYear = 108
  const currentRocYear = new Date().getFullYear() - 1911
  const endAcademicYear = currentRocYear - 1
  const options: string[] = []
  for (let year = startAcademicYear; year <= endAcademicYear; year++) {
    options.push(`${year}-1`)
    options.push(`${year}-2`)
  }
  return options
})

const hasAnyStars = computed(() =>
  form.reward > 0 || form.score > 0 || form.easiness > 0 || form.teacherStyle > 0,
)

const hasAnyOptionalInput = computed(() =>
  hasAnyStars.value
  || weeklyHoursTouched.value
  || form.textbook.trim().length > 0
  || form.comment.trim().length > 0,
)

const canSubmit = computed(() => form.semester !== '' && hasAnyOptionalInput.value)

const submitButtonText = computed(() => {
  if (form.semester === '')
    return '請先選擇修課年份'
  if (!hasAnyOptionalInput.value)
    return '請至少再填寫一項'
  return '送出評價'
})

const weeklyHoursLabel = computed(() => {
  if (!weeklyHoursTouched.value)
    return '—'
  if (form.weeklyHours <= 1)
    return '< 1h'
  if (form.weeklyHours >= 20)
    return '> 20h'
  return `${form.weeklyHours}h`
})

function handleSliderInput() {
  weeklyHoursTouched.value = true
}

function handleSubmit() {
  if (!canSubmit.value) {
    return
  }
  const normalizedComment = form.comment.trim()
  const generatedContent = normalizedComment || [
    `修課學期：${form.semester}`,
    `每週投入：約 ${weeklyHoursLabel.value}`,
    `教材：${form.textbook.trim() || '未填寫'}`,
  ].join('；')
  emit('submit', {
    title: `[${form.semester}] ${courseName}`,
    content: generatedContent,
    ratings: {
      reward: form.reward,
      score: form.score,
      easiness: form.easiness,
      teacherStyle: form.teacherStyle,
    },
    weeklyHours: weeklyHoursLabel.value,
    textbook: form.textbook.trim(),
    semester: form.semester,
  })
  submitted.value = true
}

function handleOverlayClick(e: MouseEvent) {
  if ((e.target as HTMLElement).classList.contains('review-overlay')) {
    emit('close')
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="review-fade">
      <div
        v-show="true"
        class="review-overlay"
        @click="handleOverlayClick"
      >
        <div class="review-toast" role="dialog" :aria-label="`撰寫 ${courseName} 評價`">
          <!-- Header (fixed outside scroll area) -->
          <div class="review-toast__header">
            <h3 class="review-toast__title">
              撰寫評價
            </h3>
            <button
              class="review-toast__close"
              type="button"
              aria-label="關閉"
              @click="emit('close')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Scrollable body -->
          <div class="review-toast__body">
            <Transition name="review-fade" mode="out-in">
              <div v-if="submitted" key="success" class="review-toast__success">
                <div class="review-toast__success-icon">
                  ✓
                </div>
                <p class="review-toast__success-text">
                  你的回饋已影響本課程的 AI 摘要，正在幫助其他同學更快了解這門課。
                </p>
                <button class="review-toast__done-btn" type="button" @click="emit('close')">
                  完成
                </button>
              </div>

              <form v-else key="form" class="review-toast__form" @submit.prevent="handleSubmit">
                <fieldset class="review-toast__section" :class="{ 'review-toast__section--filled': form.semester !== '' }">
                  <legend class="review-toast__legend">
                    修課年份
                    <span v-if="form.semester !== ''" class="review-toast__check">✓</span>
                  </legend>
                  <select v-model="form.semester" class="review-toast__select" aria-label="修課年份" required>
                    <option value="">
                      請選擇修課學期
                    </option>
                    <option v-for="semester in semesterOptions" :key="semester" :value="semester">
                      {{ semester }}
                    </option>
                  </select>
                </fieldset>

                <!-- Star ratings -->
                <fieldset class="review-toast__section" :class="{ 'review-toast__section--filled': hasAnyStars }">
                  <legend class="review-toast__legend">
                    星星評價
                    <span v-if="hasAnyStars" class="review-toast__check">✓</span>
                  </legend>
                  <div class="review-toast__stars-group">
                    <StarRatingInput v-model="form.reward" label="收穫" />
                    <StarRatingInput v-model="form.score" label="分數" />
                    <StarRatingInput v-model="form.easiness" label="輕鬆" />
                    <StarRatingInput v-model="form.teacherStyle" label="教師風格" />
                  </div>
                </fieldset>

                <!-- Weekly hours slider -->
                <fieldset class="review-toast__section" :class="{ 'review-toast__section--filled': weeklyHoursTouched }">
                  <legend class="review-toast__legend">
                    每週額外投入時間
                    <span v-if="weeklyHoursTouched" class="review-toast__check">✓</span>
                  </legend>
                  <div class="review-toast__slider-wrap" :class="{ 'review-toast__slider-wrap--dormant': !weeklyHoursTouched }">
                    <input
                      v-model.number="form.weeklyHours"
                      type="range"
                      min="1"
                      max="20"
                      step="1"
                      class="review-toast__slider"
                      aria-label="每週額外投入時間"
                      @input="handleSliderInput"
                    >
                    <span class="review-toast__slider-value">{{ weeklyHoursLabel }}</span>
                  </div>
                  <div class="review-toast__slider-labels">
                    <span>&lt; 1h</span>
                    <span>&gt; 20h</span>
                  </div>
                </fieldset>

                <!-- Textbook -->
                <fieldset class="review-toast__section" :class="{ 'review-toast__section--filled': form.textbook.trim().length > 0 }">
                  <legend class="review-toast__legend">
                    教科書
                    <span v-if="form.textbook.trim().length > 0" class="review-toast__check">✓</span>
                  </legend>
                  <input
                    v-model="form.textbook"
                    type="text"
                    class="review-toast__input"
                    placeholder="e.g. 書名 / 自編講義 / 無"
                  >
                </fieldset>

                <!-- Comment -->
                <fieldset class="review-toast__section" :class="{ 'review-toast__section--filled': form.comment.trim().length > 0 }">
                  <legend class="review-toast__legend">
                    任何文字說明
                    <span v-if="form.comment.trim().length > 0" class="review-toast__check">✓</span>
                  </legend>
                  <textarea
                    v-model="form.comment"
                    class="review-toast__textarea"
                    rows="3"
                    placeholder="分享你的修課經驗，任意格式皆可…"
                  />
                </fieldset>

                <button
                  type="submit"
                  class="review-toast__submit"
                  :class="{ 'review-toast__submit--disabled': !canSubmit }"
                  :disabled="!canSubmit"
                >
                  {{ submitButtonText }}
                </button>
              </form>
            </Transition>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Overlay */
.review-overlay {
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

/* Toast card */
.review-toast {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  width: 100%;
  max-width: 460px;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Header */
.review-toast__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg) var(--spacing-xl) 0;
  flex-shrink: 0;
}

/* Scrollable body */
.review-toast__body {
  overflow-y: auto;
  padding: var(--spacing-lg) var(--spacing-xl) var(--spacing-lg);
}

.review-toast__title {
  font-size: var(--font-size-xl);
  font-weight: 800;
  color: var(--color-text-primary);
}

.review-toast__close {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
}

.review-toast__close:hover {
  color: var(--color-text-primary);
  background: var(--color-background-alt);
}

.review-toast__close svg {
  width: 18px;
  height: 18px;
}

/* Form sections */
.review-toast__form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.review-toast__section {
  border: none;
  padding: 0;
  transition: opacity var(--transition-fast);
}

.review-toast__section--filled {
  opacity: 1;
}

.review-toast__legend {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
  display: flex;
  align-items: center;
  gap: 6px;
}

.review-toast__check {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-accent-secondary);
  background: rgba(168, 197, 181, 0.15);
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Star ratings group */
.review-toast__stars-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* Slider */
.review-toast__slider-wrap {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.review-toast__slider {
  flex: 1;
  -webkit-appearance: none;
  appearance: none;
  height: 6px;
  border-radius: var(--radius-full);
  background: var(--color-background-alt);
  outline: none;
  transition: background var(--transition-fast);
}

.review-toast__slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--color-accent-primary);
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  transition: transform var(--transition-fast);
}

.review-toast__slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}

.review-toast__slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--color-accent-primary);
  cursor: pointer;
  border: none;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.review-toast__slider-value {
  min-width: 44px;
  text-align: center;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-accent-primary);
}

.review-toast__slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin-top: 2px;
  padding: 0 2px;
}

/* Text input */
.review-toast__input {
  width: 100%;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--color-background-alt);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  transition: box-shadow var(--transition-fast);
}

.review-toast__input::placeholder {
  color: var(--color-text-muted);
}

.review-toast__input:focus {
  box-shadow: 0 0 0 2px var(--color-accent-primary);
}

.review-toast__select {
  width: 100%;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--color-background-alt);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  border: none;
  outline: none;
  transition: box-shadow var(--transition-fast);
}

.review-toast__select:focus {
  box-shadow: 0 0 0 2px var(--color-accent-primary);
}

/* Textarea */
.review-toast__textarea {
  width: 100%;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--color-background-alt);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  resize: vertical;
  min-height: 72px;
  line-height: 1.6;
  transition: box-shadow var(--transition-fast);
}

.review-toast__textarea::placeholder {
  color: var(--color-text-muted);
}

.review-toast__textarea:focus {
  box-shadow: 0 0 0 2px var(--color-accent-primary);
}

/* Dormant slider (not yet touched) */
.review-toast__slider-wrap--dormant {
  opacity: 0.45;
}

.review-toast__slider-wrap--dormant .review-toast__slider::-webkit-slider-thumb {
  background: var(--color-text-muted);
}

.review-toast__slider-wrap--dormant .review-toast__slider::-moz-range-thumb {
  background: var(--color-text-muted);
}

/* Submit button */
.review-toast__submit {
  width: 100%;
  padding: 12px;
  border-radius: var(--radius-full);
  background: var(--color-accent-primary);
  color: white;
  font-weight: 600;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.review-toast__submit:hover:not(:disabled) {
  background: var(--color-text-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.review-toast__submit--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Success state */
.review-toast__success {
  text-align: center;
  padding: var(--spacing-xl) 0;
}

.review-toast__success-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--spacing-md);
  border-radius: 50%;
  background: var(--color-accent-secondary);
  color: white;
  font-size: var(--font-size-xl);
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.review-toast__success-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.7;
  max-width: 320px;
  margin: 0 auto var(--spacing-lg);
}

.review-toast__done-btn {
  padding: 10px var(--spacing-xl);
  border-radius: var(--radius-full);
  background: var(--color-accent-primary);
  color: white;
  font-weight: 600;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.review-toast__done-btn:hover {
  background: var(--color-text-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Transitions */
.review-fade-enter-active,
.review-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.review-fade-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.97);
}

.review-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
}

/* Responsive */
@media (max-width: 520px) {
  .review-toast {
    max-width: 100%;
    border-radius: var(--radius-lg);
  }

  .review-toast__header {
    padding: var(--spacing-md) var(--spacing-lg) 0;
  }

  .review-toast__body {
    padding: var(--spacing-md) var(--spacing-lg) var(--spacing-md);
  }
}
</style>
