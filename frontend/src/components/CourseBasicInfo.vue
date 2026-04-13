<script setup lang="ts">
import type { Course } from '@/types'
import { computed } from 'vue'

const props = defineProps<{
  course: Course
}>()

const COURSE_TIME_TOKEN_REGEX = /^([^\d\s]+)\s*(\d+)$/

const formattedTime = computed(() => formatCourseTime(props.course.time))
const localizedType = computed(() => localizeCourseType(props.course.type))

function formatCourseTime(rawTime: string | null | undefined): string {
  if (!rawTime)
    return '—'

  const tokens = rawTime
    .split('/')
    .map(token => token.trim())
    .filter(Boolean)

  const dayMap = new Map<string, string[]>()

  for (const token of tokens) {
    const match = token.match(COURSE_TIME_TOKEN_REGEX)
    if (!match)
      continue

    const day = match[1]
    const period = match[2]
    const periods = dayMap.get(day) ?? []
    periods.push(period)
    dayMap.set(day, periods)
  }

  if (!dayMap.size)
    return rawTime

  return Array.from(dayMap.entries())
    .map(([day, periods]) => `${day} ${periods.join(', ')}`)
    .join(' / ')
}

function localizeCourseType(type: string | null | undefined): string {
  if (!type)
    return '—'

  const upperType = type.toUpperCase()
  if (upperType === 'REQUIRED')
    return '必修'
  if (upperType === 'ELECTIVE')
    return '選修'
  return type
}
</script>

<template>
  <section class="basic-info" aria-label="課程基本資訊">
    <h2 class="basic-info__title">
      課程基本資訊
    </h2>

    <div class="basic-info__cards">
      <div class="basic-info__card">
        <span class="basic-info__label">系所：</span>
        <span class="basic-info__value">{{ course.department ?? '—' }}</span>
      </div>
      <div class="basic-info__card">
        <span class="basic-info__label">課號：</span>
        <span class="basic-info__value">{{ course.code ?? '—' }}</span>
      </div>
      <div class="basic-info__card">
        <span class="basic-info__label">教師：</span>
        <span class="basic-info__value">{{ course.teacher ?? '—' }}</span>
      </div>
      <div class="basic-info__card">
        <span class="basic-info__label">上課時間：</span>
        <span class="basic-info__value">{{ formattedTime }}</span>
      </div>
      <div class="basic-info__card">
        <span class="basic-info__label">學分數：</span>
        <span class="basic-info__value">{{ course.credits ?? '—' }}</span>
      </div>
      <div class="basic-info__card">
        <span class="basic-info__label">必修 / 選修：</span>
        <span class="basic-info__value">{{ localizedType }}</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.basic-info {
  padding: var(--spacing-lg);
  border-radius: var(--radius-xl);
  background:
    radial-gradient(circle at 5% 95%, rgba(203, 239, 242, 0.38), transparent 32%),
    radial-gradient(circle at 95% 8%, rgba(229, 238, 255, 0.42), transparent 30%),
    rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  box-shadow: var(--shadow-lg);
}

.basic-info__title {
  font-size: var(--font-size-xl);
  font-weight: 800;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
  letter-spacing: 0.03em;
  text-align: center;
}

.basic-info__cards {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.basic-info__card {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-surface);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-sm);
  white-space: nowrap;
  overflow: hidden;
}

.basic-info__label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  flex-shrink: 0;
}

.basic-info__value {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
