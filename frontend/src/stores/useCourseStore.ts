import type { Course, CourseRatings, SortCriterion } from '@/types'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getCourseById, getCourses } from '@/api/courses'

function getSortValue(course: Course, field: SortCriterion['field']): number {
  if (!course.ratings)
    return 0
  if (field === 'overall') {
    const { easiness, reward, score, teacherStyle } = course.ratings
    return (reward + score + easiness + teacherStyle) / 4
  }
  return course.ratings[field]
}

export const useCourseStore = defineStore('course', () => {
  const courses = ref<Course[]>([])
  const selectedCourse = ref<Course | null>(null)
  const searchQuery = ref('')
  const sortCriteria = ref<SortCriterion[]>([
    { field: 'overall', label: '綜合平均', direction: 'desc', enabled: false },
    { field: 'reward', label: '收穫', direction: 'desc', enabled: false },
    { field: 'score', label: '分數', direction: 'desc', enabled: false },
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
      const sort = active ? `${active.field}:${active.direction}` : undefined
      courses.value = await getCourses({ q: searchQuery.value, sort })
    }
    finally {
      isLoading.value = false
    }
  }

  async function fetchCourseById(courseId: number): Promise<void> {
    isLoading.value = true
    try {
      selectedCourse.value = await getCourseById(courseId)
    }
    finally {
      isLoading.value = false
    }
  }

  function setSearchQuery(query: string): void {
    searchQuery.value = query
  }

  function setSortCriteria(criteria: SortCriterion[]): void {
    sortCriteria.value = criteria
  }

  function applyReviewRatings(courseId: number, nextRatings: CourseRatings): void {
    const target = courses.value.find(course => course.id === courseId)
    if (target) {
      target.ratings = { ...nextRatings }
      if (target.summary) {
        target.summary.reviewCount += 1
      }
    }
    if (selectedCourse.value?.id === courseId) {
      selectedCourse.value.ratings = { ...nextRatings }
      if (selectedCourse.value.summary) {
        selectedCourse.value.summary.reviewCount += 1
      }
    }
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
    setSearchQuery,
    setSortCriteria,
    sortCriteria,
  }
})
