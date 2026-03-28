<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ApiError } from '@/api/client'
import wishingAnimation from '@/assets/wishing_animation_3s.mp4'
import { useCoursePairsStore } from '@/stores/useCoursePairsStore'
import { useWishStore } from '@/stores/useWishStore'

interface WishFormPayload {
  name: string
  teacher: string
}

type SubmissionState = 'idle' | 'submitting' | 'success' | 'failure'

const emit = defineEmits<{
  close: []
  submit: [payload: WishFormPayload]
}>()

const pairsStore = useCoursePairsStore()
const wishStore = useWishStore()

const form = reactive<WishFormPayload>({
  name: '',
  teacher: '',
})

const submissionState = ref<SubmissionState>('idle')
const failureReason = ref('')

onMounted(async () => {
  await pairsStore.fetchPairs()
})

const filteredCourseNames = computed(() => {
  const teacher = form.teacher.trim()
  if (teacher) {
    return pairsStore.getCourseNamesByTeacher(teacher).slice(0, 12)
  }
  const keyword = form.name.trim().toLowerCase()
  if (!keyword)
    return pairsStore.getCourseNamesByTeacher('').slice(0, 12)
  return pairsStore
    .getCourseNamesByTeacher('')
    .filter(n => n.toLowerCase().includes(keyword))
    .slice(0, 12)
})

const filteredTeachers = computed(() => {
  const name = form.name.trim()
  if (name) {
    return pairsStore.getTeachersByCourseName(name).slice(0, 12)
  }
  const keyword = form.teacher.trim().toLowerCase()
  if (!keyword)
    return pairsStore.getTeachersByCourseName('').slice(0, 12)
  return pairsStore
    .getTeachersByCourseName('')
    .filter(t => t.toLowerCase().includes(keyword))
    .slice(0, 12)
})

const canSubmit = computed(() => {
  const name = form.name.trim()
  const teacher = form.teacher.trim()
  return name.length > 0 && teacher.length > 0 && pairsStore.isValidPair(name, teacher)
})

function handleOverlayClick(event: MouseEvent) {
  if ((event.target as HTMLElement).classList.contains('wish-overlay')) {
    emit('close')
  }
}

async function handleSubmit() {
  if (!canSubmit.value)
    return

  const payload: WishFormPayload = {
    name: form.name.trim(),
    teacher: form.teacher.trim(),
  }
  submissionState.value = 'submitting'
  failureReason.value = ''
  try {
    await wishStore.createWish(payload)
    submissionState.value = 'success'
    emit('submit', payload)
  }
  catch (e) {
    submissionState.value = 'failure'
    failureReason.value = e instanceof ApiError ? e.message : '許願失敗，請稍後再試'
  }
}

function handleRetry() {
  submissionState.value = 'idle'
  failureReason.value = ''
}
</script>

<template>
  <Teleport to="body">
    <Transition name="wish-fade">
      <div v-show="true" class="wish-overlay" @click="handleOverlayClick">
        <div class="wish-toast" role="dialog" aria-label="課程許願池表單">
          <div v-if="submissionState !== 'success'" class="wish-toast__header">
            <h3 class="wish-toast__title">
              課程許願池
            </h3>
            <button
              class="wish-toast__close"
              type="button"
              aria-label="關閉"
              @click="emit('close')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="wish-toast__body">
            <Transition name="wish-fade" mode="out-in">
              <div
                v-if="submissionState === 'success'"
                key="success"
                class="wish-toast__result wish-toast__result--success"
                role="status"
                aria-live="polite"
              >
                <h3 class="wish-toast__success-title">
                  課程女神眷顧我
                </h3>
                <video
                  class="wish-toast__video"
                  :src="wishingAnimation"
                  autoplay
                  muted
                  playsinline
                />
                <button class="wish-toast__result-btn" type="button" @click="emit('close')">
                  太棒了！
                </button>
              </div>
              <div
                v-else-if="submissionState === 'failure'"
                key="failure"
                class="wish-toast__result wish-toast__result--failure"
                role="alert"
                aria-live="assertive"
              >
                <div class="wish-toast__result-icon wish-toast__result-icon--failure">
                  ✕
                </div>
                <p class="wish-toast__result-text">
                  許願失敗
                </p>
                <p v-if="failureReason" class="wish-toast__result-reason">
                  {{ failureReason }}
                </p>
                <div class="wish-toast__result-actions">
                  <button class="wish-toast__result-btn wish-toast__result-btn--secondary" type="button" @click="handleRetry">
                    再試一次
                  </button>
                  <button class="wish-toast__result-btn" type="button" @click="emit('close')">
                    關閉
                  </button>
                </div>
              </div>
              <form
                v-else
                key="form"
                class="wish-toast__form"
                @submit.prevent="handleSubmit"
              >
                <label class="wish-toast__label" for="wish-course-name">
                  許願課程名稱
                </label>
                <input
                  id="wish-course-name"
                  v-model="form.name"
                  type="text"
                  list="wish-course-name-options"
                  class="wish-toast__input"
                  placeholder="請輸入課程名稱"
                >
                <datalist id="wish-course-name-options">
                  <option
                    v-for="courseName in filteredCourseNames"
                    :key="courseName"
                    :value="courseName"
                  />
                </datalist>

                <label class="wish-toast__label" for="wish-course-teacher">
                  授課教師
                </label>
                <input
                  id="wish-course-teacher"
                  v-model="form.teacher"
                  type="text"
                  list="wish-course-teacher-options"
                  class="wish-toast__input"
                  placeholder="請輸入教師姓名"
                >
                <datalist id="wish-course-teacher-options">
                  <option
                    v-for="teacher in filteredTeachers"
                    :key="teacher"
                    :value="teacher"
                  />
                </datalist>

                <p v-if="form.name.trim() && form.teacher.trim() && !canSubmit" class="wish-toast__hint">
                  此課程與教師的組合不存在
                </p>

                <button
                  type="submit"
                  class="wish-toast__submit"
                  :class="{ 'wish-toast__submit--disabled': !canSubmit || submissionState === 'submitting' }"
                  :disabled="!canSubmit || submissionState === 'submitting'"
                >
                  {{ submissionState === 'submitting' ? '送出中…' : '送出許願' }}
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
.wish-overlay {
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

.wish-toast {
  width: 100%;
  max-width: 420px;
  border-radius: var(--radius-xl);
  background: var(--color-surface);
  box-shadow: var(--shadow-xl);
  padding: var(--spacing-lg) var(--spacing-xl);
}

.wish-toast__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.wish-toast__title {
  font-size: var(--font-size-xl);
  font-weight: 800;
  color: var(--color-text-primary);
}

.wish-toast__close {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  transition: all var(--transition-fast);
}

.wish-toast__close:hover {
  color: var(--color-text-primary);
  background: var(--color-background-alt);
}

.wish-toast__close svg {
  width: 18px;
  height: 18px;
}

.wish-toast__form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.wish-toast__label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
}

.wish-toast__input {
  width: 100%;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--color-background-alt);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
  transition: box-shadow var(--transition-fast);
}

.wish-toast__input::placeholder {
  color: var(--color-text-muted);
}

.wish-toast__input:focus {
  box-shadow: 0 0 0 2px var(--color-accent-primary);
}

.wish-toast__hint {
  font-size: var(--font-size-xs);
  color: var(--color-danger, #e53e3e);
  margin: 0;
}

.wish-toast__submit {
  margin-top: var(--spacing-sm);
  width: 100%;
  padding: 12px;
  border-radius: var(--radius-full);
  background: var(--color-accent-primary);
  color: white;
  font-size: var(--font-size-sm);
  font-weight: 600;
  transition: all var(--transition-fast);
}

.wish-toast__submit:hover:not(:disabled) {
  background: var(--color-text-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.wish-toast__submit--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Result state (animation-ready: add keyframes to --success / --failure later) */
.wish-toast__body {
  min-height: 120px;
}

.wish-toast__result {
  text-align: center;
  padding: var(--spacing-xl) 0;
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}

.wish-toast__result--success {
  padding: 0;
}

.wish-toast__video {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: var(--radius-md);
  display: block;
  margin: 0 auto var(--spacing-md);
}

.wish-toast__success-title {
  font-size: var(--font-size-xl);
  font-weight: 800;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
}

.wish-toast__result--failure {
  /* reserved for future failure animation */
}

.wish-toast__result-icon {
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
  transition: transform var(--transition-fast);
}

.wish-toast__result-icon--failure {
  background: var(--color-danger, #e53e3e);
}

.wish-toast__result-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.7;
  margin: 0 auto var(--spacing-sm);
}

.wish-toast__result-reason {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  line-height: 1.5;
  margin: 0 auto var(--spacing-md);
  max-width: 320px;
}

.wish-toast__result-actions {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: center;
  flex-wrap: wrap;
  margin-top: var(--spacing-md);
}

.wish-toast__result-btn {
  padding: 10px var(--spacing-xl);
  border-radius: var(--radius-full);
  background: var(--color-accent-primary);
  color: white;
  font-weight: 600;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.wish-toast__result-btn:hover {
  background: var(--color-text-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.wish-toast__result-btn--secondary {
  background: var(--color-background-alt);
  color: var(--color-text-primary);
}

.wish-toast__result-btn--secondary:hover {
  background: var(--color-text-muted);
  color: white;
}

.wish-fade-enter-active,
.wish-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.wish-fade-enter-from,
.wish-fade-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}
</style>
