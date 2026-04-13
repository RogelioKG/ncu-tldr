<script setup lang="ts">
import { useFocusTrap } from '@vueuse/integrations/useFocusTrap'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import wishingAnimation from '@/assets/wishing_animation_3s.mp4'
import ErrorToast from '@/components/ErrorToast.vue'
import { useFormValidation } from '@/composables/useFormValidation'
import { wishFormSchema } from '@/schemas'
import { useCoursePairsStore } from '@/stores/useCoursePairsStore'
import { useWishStore } from '@/stores/useWishStore'

type SubmissionState = 'idle' | 'submitting' | 'success'

const emit = defineEmits<{
  close: []
}>()

const pairsStore = useCoursePairsStore()
const wishStore = useWishStore()

const { form, errors, validateAll, touchField, getFieldError } = useFormValidation(
  wishFormSchema,
  { name: '', teacher: '' },
)

const submissionState = ref<SubmissionState>('idle')
const showErrorToast = ref(false)
const showCourseDropdown = ref(false)
const showTeacherDropdown = ref(false)
const dialogRef = ref<HTMLElement | null>(null)
const { activate, deactivate } = useFocusTrap(dialogRef)

onMounted(async () => {
  await pairsStore.fetchPairs()
  activate()
})

onUnmounted(() => deactivate())

const filteredCourseNames = computed(() => {
  const teacher = form.teacher.trim()
  const courseKeyword = form.name.trim().toLowerCase()
  const exactTeacherMatch = teacher.length > 0 && pairsStore.pairs.some(p => p.teacher === teacher)
  if (exactTeacherMatch) {
    const courses = [...new Set(pairsStore.pairs.filter(p => p.teacher === teacher).map(p => p.courseName))]
    if (!courseKeyword)
      return courses.slice(0, 12)
    return courses.filter(n => n.toLowerCase().includes(courseKeyword)).slice(0, 12)
  }
  if (!courseKeyword)
    return pairsStore.getCourseNamesByTeacher('').slice(0, 12)
  return pairsStore.getCourseNamesByTeacher('').filter(n => n.toLowerCase().includes(courseKeyword)).slice(0, 12)
})

const filteredTeachers = computed(() => {
  const name = form.name.trim()
  const teacherKeyword = form.teacher.trim().toLowerCase()
  const exactCourseMatch = name.length > 0 && pairsStore.pairs.some(p => p.courseName === name)
  if (exactCourseMatch) {
    const teachers = [...new Set(pairsStore.pairs.filter(p => p.courseName === name).map(p => p.teacher))]
    if (!teacherKeyword)
      return teachers.slice(0, 12)
    return teachers.filter(t => t.toLowerCase().includes(teacherKeyword)).slice(0, 12)
  }
  if (!teacherKeyword)
    return pairsStore.getTeachersByCourseName('').slice(0, 12)
  return pairsStore.getTeachersByCourseName('').filter(t => t.toLowerCase().includes(teacherKeyword)).slice(0, 12)
})

const canSubmit = computed(() => {
  const name = form.name.trim()
  const teacher = form.teacher.trim()
  return name.length > 0 && teacher.length > 0 && pairsStore.isValidPair(name, teacher)
})

function selectCourseName(name: string) {
  form.name = name
  showCourseDropdown.value = false
  touchField('name')
}

function selectTeacher(teacher: string) {
  form.teacher = teacher
  showTeacherDropdown.value = false
  touchField('teacher')
}

function onCourseNameBlur() {
  touchField('name')
  setTimeout(() => {
    showCourseDropdown.value = false
  }, 150)
}

function onTeacherBlur() {
  touchField('teacher')
  setTimeout(() => {
    showTeacherDropdown.value = false
  }, 150)
}

function handleOverlayClick(event: MouseEvent) {
  if ((event.target as HTMLElement).classList.contains('wish-overlay'))
    emit('close')
}

async function handleSubmit() {
  if (!validateAll())
    return

  const name = form.name.trim()
  const teacher = form.teacher.trim()

  if (!pairsStore.isValidPair(name, teacher)) {
    errors._form = '此課程與教師的組合不存在，請重新選擇'
    return
  }

  const courseId = pairsStore.getCourseIdByPair(name, teacher)
  if (courseId === undefined) {
    errors._form = '找不到對應課程，請重新選擇'
    return
  }

  submissionState.value = 'submitting'
  try {
    await wishStore.voteForCourseById(courseId)
    submissionState.value = 'success'
  }
  catch {
    submissionState.value = 'idle'
    showErrorToast.value = true
  }
}
</script>

<template>
  <ErrorToast :visible="showErrorToast" @close="showErrorToast = false" />
  <Teleport to="body">
    <Transition name="wish-fade">
      <div v-if="true" class="wish-overlay" @click="handleOverlayClick">
        <div ref="dialogRef" class="wish-toast" role="dialog" aria-label="課程許願池表單">
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
              <form
                v-else
                key="form"
                class="wish-toast__form"
                @submit.prevent="handleSubmit"
              >
                <label class="wish-toast__label" for="wish-course-name">
                  許願課程名稱
                </label>
                <div class="wish-toast__field-wrapper">
                  <input
                    id="wish-course-name"
                    v-model="form.name"
                    type="text"
                    class="wish-toast__input"
                    :class="{ 'wish-toast__input--error': getFieldError('name') }"
                    placeholder="請輸入課程名稱"
                    autocomplete="off"
                    @focus="showCourseDropdown = true"
                    @blur="onCourseNameBlur"
                    @keydown.escape="showCourseDropdown = false"
                  >
                  <ul
                    v-if="showCourseDropdown && filteredCourseNames.length > 0"
                    class="wish-toast__dropdown"
                    role="listbox"
                    aria-label="課程名稱選項"
                  >
                    <li
                      v-for="courseName in filteredCourseNames"
                      :key="courseName"
                      class="wish-toast__dropdown-option"
                      role="option"
                      @mousedown.prevent="selectCourseName(courseName)"
                    >
                      {{ courseName }}
                    </li>
                  </ul>
                </div>
                <p v-if="getFieldError('name')" class="wish-toast__field-error">
                  {{ getFieldError('name') }}
                </p>

                <label class="wish-toast__label" for="wish-course-teacher">
                  授課教師
                </label>
                <div class="wish-toast__field-wrapper">
                  <input
                    id="wish-course-teacher"
                    v-model="form.teacher"
                    type="text"
                    class="wish-toast__input"
                    :class="{ 'wish-toast__input--error': getFieldError('teacher') }"
                    placeholder="請輸入教師姓名"
                    autocomplete="off"
                    @focus="showTeacherDropdown = true"
                    @blur="onTeacherBlur"
                    @keydown.escape="showTeacherDropdown = false"
                  >
                  <ul
                    v-if="showTeacherDropdown && filteredTeachers.length > 0"
                    class="wish-toast__dropdown"
                    role="listbox"
                    aria-label="教師名稱選項"
                  >
                    <li
                      v-for="teacher in filteredTeachers"
                      :key="teacher"
                      class="wish-toast__dropdown-option"
                      role="option"
                      @mousedown.prevent="selectTeacher(teacher)"
                    >
                      {{ teacher }}
                    </li>
                  </ul>
                </div>
                <p v-if="getFieldError('teacher')" class="wish-toast__field-error">
                  {{ getFieldError('teacher') }}
                </p>

                <p v-if="errors._form" class="wish-toast__field-error">
                  {{ errors._form }}
                </p>

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

.wish-toast__field-wrapper {
  position: relative;
}

.wish-toast__input {
  width: 100%;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--color-background-alt);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  transition: box-shadow var(--transition-fast);
}

.wish-toast__input::placeholder {
  color: var(--color-text-muted);
}

.wish-toast__input:focus {
  box-shadow: 0 0 0 2px var(--color-accent-primary);
}

.wish-toast__input--error {
  border-color: var(--color-error, #c0392b);
  box-shadow: 0 0 0 2px rgba(192, 57, 43, 0.12);
}

.wish-toast__dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  z-index: 10;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  max-height: 200px;
  overflow-y: auto;
  padding: var(--spacing-xs) 0;
  list-style: none;
}

.wish-toast__dropdown-option {
  padding: 8px 14px;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.wish-toast__dropdown-option:hover {
  background: var(--color-background-alt);
}

.wish-toast__field-error {
  margin-top: calc(var(--spacing-xs) * -1);
  font-size: var(--font-size-xs);
  color: var(--color-error, #c0392b);
}

.wish-toast__hint {
  font-size: var(--font-size-xs);
  color: var(--color-error, #e53e3e);
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

.wish-toast__result-btn {
  margin-top: var(--spacing-md);
  width: 100%;
  padding: 12px;
  border-radius: var(--radius-full);
  background: var(--color-accent-primary);
  color: white;
  font-size: var(--font-size-sm);
  font-weight: 600;
  transition: all var(--transition-fast);
}

.wish-toast__result-btn:hover {
  background: var(--color-text-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
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
