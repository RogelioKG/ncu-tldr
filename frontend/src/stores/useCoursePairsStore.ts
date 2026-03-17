import { defineStore } from 'pinia'
import { ref } from 'vue'
import { hasBackendApi, request } from '@/api/client'
import { mockCourses } from '@/mock/courses'

interface CoursePair {
  courseName: string
  teacher: string
}

interface CoursePairsResponse {
  pairs: CoursePair[]
}

export const useCoursePairsStore = defineStore('coursePairs', () => {
  const pairs = ref<CoursePair[]>([])
  const fetched = ref(false)
  const isLoading = ref(false)

  async function fetchPairs(): Promise<void> {
    if (fetched.value)
      return
    isLoading.value = true
    try {
      if (hasBackendApi()) {
        const data = await request<CoursePairsResponse>('/api/courses/pairs')
        pairs.value = data.pairs
      }
      else {
        pairs.value = mockCourses.map(c => ({ courseName: c.name, teacher: c.teacher }))
      }
      fetched.value = true
    }
    finally {
      isLoading.value = false
    }
  }

  function getTeachersByCourseName(name: string): string[] {
    const keyword = name.trim().toLowerCase()
    if (!keyword)
      return [...new Set(pairs.value.map(p => p.teacher))]
    return [
      ...new Set(
        pairs.value
          .filter(p => p.courseName.toLowerCase().includes(keyword))
          .map(p => p.teacher),
      ),
    ]
  }

  function getCourseNamesByTeacher(teacher: string): string[] {
    const keyword = teacher.trim().toLowerCase()
    if (!keyword)
      return [...new Set(pairs.value.map(p => p.courseName))]
    return [
      ...new Set(
        pairs.value
          .filter(p => p.teacher.toLowerCase().includes(keyword))
          .map(p => p.courseName),
      ),
    ]
  }

  function isValidPair(name: string, teacher: string): boolean {
    return pairs.value.some(
      p => p.courseName === name && p.teacher === teacher,
    )
  }

  return {
    fetchPairs,
    getCourseNamesByTeacher,
    getTeachersByCourseName,
    isLoading,
    isValidPair,
    pairs,
  }
})
