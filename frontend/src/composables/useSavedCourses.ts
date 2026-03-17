import type { Course } from '@/types'
import { computed, ref } from 'vue'
import { mockCourses } from '@/mock/courses'

export interface SavedCourseEntry {
  courseId: number
  order: number
}

const savedEntries = ref<SavedCourseEntry[]>([])

export function useSavedCourses() {
  const savedCourses = computed<Course[]>(() => {
    const sorted = savedEntries.value.toSorted((a, b) => a.order - b.order)
    return sorted
      .map(entry => mockCourses.find(c => c.id === entry.courseId))
      .filter((c): c is Course => c !== undefined)
  })

  const savedCourseIds = computed(() =>
    new Set(savedEntries.value.map(e => e.courseId)),
  )

  function isSaved(courseId: number): boolean {
    return savedCourseIds.value.has(courseId)
  }

  function toggleSave(courseId: number) {
    const idx = savedEntries.value.findIndex(e => e.courseId === courseId)
    if (idx >= 0) {
      savedEntries.value.splice(idx, 1)
      reindex()
    }
    else {
      savedEntries.value.push({
        courseId,
        order: savedEntries.value.length,
      })
    }
  }

  function moveUp(courseId: number) {
    const sorted = savedEntries.value.toSorted((a, b) => a.order - b.order)
    const idx = sorted.findIndex(e => e.courseId === courseId)
    if (idx <= 0)
      return
    const prev = sorted[idx - 1]!
    const curr = sorted[idx]!
    const tmpOrder = curr.order
    curr.order = prev.order
    prev.order = tmpOrder
    savedEntries.value = [...sorted]
  }

  function moveDown(courseId: number) {
    const sorted = savedEntries.value.toSorted((a, b) => a.order - b.order)
    const idx = sorted.findIndex(e => e.courseId === courseId)
    if (idx < 0 || idx >= sorted.length - 1)
      return
    const next = sorted[idx + 1]!
    const curr = sorted[idx]!
    const tmpOrder = curr.order
    curr.order = next.order
    next.order = tmpOrder
    savedEntries.value = [...sorted]
  }

  function reindex() {
    const sorted = savedEntries.value.toSorted((a, b) => a.order - b.order)
    sorted.forEach((entry, i) => {
      entry.order = i
    })
    savedEntries.value = sorted
  }

  return {
    savedCourses,
    savedCourseIds,
    isSaved,
    toggleSave,
    moveUp,
    moveDown,
  }
}
