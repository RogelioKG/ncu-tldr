import type { Course, CourseRatings, SortCriterion, TimeSlot } from '@/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getCourseById, getCourses } from '@/api/courses'

// Sort param mapping: backend SORT_MAP uses reward/score as keys even though it returns gain/highScore
const SORT_PARAM_MAP: Record<string, string> = {
  gain: 'reward',
  highScore: 'score',
}

function getSortValue(course: Course, field: SortCriterion['field']): number {
  if (!course.ratings)
    return 0
  if (field === 'overall') {
    const { easiness, gain, highScore, teacherStyle } = course.ratings
    return (gain + highScore + easiness + teacherStyle) / 4
  }
  return course.ratings[field]
}

export const useCourseStore = defineStore('course', () => {
  const courses = ref<Course[]>([])
  const selectedCourseId = ref<number | null>(null)
  const selectedCourse = computed<Course | null>(() =>
    courses.value.find(c => c.id === selectedCourseId.value) ?? null,
  )
  const searchQuery = ref('')
  const selectedSlots = ref<TimeSlot[]>([])
  const sortCriteria = ref<SortCriterion[]>([
    { field: 'overall', label: '綜合平均', direction: 'desc', enabled: false },
    { field: 'gain', label: '收穫', direction: 'desc', enabled: false },
    { field: 'highScore', label: '分數', direction: 'desc', enabled: false },
    { field: 'easiness', label: '輕鬆', direction: 'desc', enabled: false },
    { field: 'teacherStyle', label: '教師風格', direction: 'desc', enabled: false },
  ])
  const isLoading = ref(false)

  const filteredCourses = computed(() => {
    const keyword = searchQuery.value.trim().toLowerCase()
    const list = keyword
      ? courses.value.filter(course =>
          course.name.toLowerCase().includes(keyword)
          || course.teacher.toLowerCase().includes(keyword)
          || course.tags.some(tag => tag.toLowerCase().includes(keyword)),
        )
      : [...courses.value]

    const activeCriteria = sortCriteria.value.filter(row => row.enabled)
    if (activeCriteria.length === 0) {
      return list.sort((a, b) => a.id - b.id)
    }
    return list.sort((a, b) => {
      for (const criterion of activeCriteria) {
        const valA = getSortValue(a, criterion.field)
        const valB = getSortValue(b, criterion.field)
        if (valA !== valB) {
          return criterion.direction === 'desc' ? valB - valA : valA - valB
        }
      }
      return 0
    })
  })

  async function fetchCourses(): Promise<void> {
    isLoading.value = true
    try {
      const active = sortCriteria.value.find(c => c.enabled)
      const sort = active
        ? `${SORT_PARAM_MAP[active.field] ?? active.field}:${active.direction}`
        : undefined
      courses.value = await getCourses({ q: searchQuery.value, sort, slots: selectedSlots.value })
    }
    finally {
      isLoading.value = false
    }
  }

  async function fetchCourseById(courseId: number): Promise<void> {
    isLoading.value = true
    try {
      const fetched = await getCourseById(courseId)
      if (fetched) {
        const idx = courses.value.findIndex(c => c.id === courseId)
        if (idx >= 0) {
          courses.value = courses.value.map(c => c.id === courseId ? fetched : c)
        }
        else {
          courses.value = [...courses.value, fetched]
        }
        selectedCourseId.value = courseId
      }
    }
    finally {
      isLoading.value = false
    }
  }

  function setSearchQuery(query: string): void {
    searchQuery.value = query
  }

  function setSelectedSlots(slots: TimeSlot[]): void {
    selectedSlots.value = slots
  }

  function setSortCriteria(criteria: SortCriterion[]): void {
    sortCriteria.value = criteria
  }

  function applyReviewRatings(courseId: number, nextRatings: CourseRatings): void {
    courses.value = courses.value.map((course) => {
      if (course.id !== courseId)
        return course
      return {
        ...course,
        ratings: { ...nextRatings },
        summary: course.summary
          ? { ...course.summary, reviewCount: course.summary.reviewCount + 1 }
          : course.summary,
      }
    })
  }

  return {
    courses,
    fetchCourseById,
    fetchCourses,
    filteredCourses,
    isLoading,
    applyReviewRatings,
    searchQuery,
    selectedCourse,
    selectedSlots,
    setSearchQuery,
    setSelectedSlots,
    setSortCriteria,
    sortCriteria,
  }
})
