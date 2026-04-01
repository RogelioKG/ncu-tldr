import type { Course } from '@/types'
import { mockCourses } from '@/mock/courses'
import { hasBackendApi, request } from './client'

export async function getCourses(params?: { q?: string, sort?: string }): Promise<Course[]> {
  if (hasBackendApi()) {
    const query = new URLSearchParams()
    if (params?.q) {
      query.set('q', params.q)
    }
    if (params?.sort) {
      query.set('sort', params.sort)
    }
    const suffix = query.toString() ? `?${query.toString()}` : ''
    return await request<Course[]>(`/courses${suffix}`)
  }

  const keyword = params?.q?.trim().toLowerCase() ?? ''
  if (!keyword) {
    return [...mockCourses]
  }
  return mockCourses.filter(course =>
    course.name.toLowerCase().includes(keyword)
    || course.teacher.toLowerCase().includes(keyword)
    || course.tags.some(tag => tag.toLowerCase().includes(keyword)),
  )
}

export async function getCourseById(courseId: number): Promise<Course | null> {
  if (hasBackendApi()) {
    try {
      return await request<Course>(`/courses/${courseId}`)
    }
    catch {
      return null
    }
  }
  return mockCourses.find(course => course.id === courseId) ?? null
}
