import type { Course } from '@/types'
import { mockCourses } from '@/mock/courses'
import { hasBackendApi, request } from './client'

/** Backend CourseOut shape returned by the API */
interface CourseTimeOut {
  day: number
  period: string
}

interface CourseOut {
  id: number
  externalId: number
  classNo: string
  title: string
  credit: number
  passwordCard: string
  limitCnt: number | null
  admitCnt: number
  waitCnt: number
  courseType: string
  lastSemester: string | null
  teachers: string[]
  departments: string[]
  colleges: string[]
  times: CourseTimeOut[]
}

const DAY_LABELS = ['', '一', '二', '三', '四', '五', '六', '日']

function formatTimes(times: CourseTimeOut[]): string {
  if (times.length === 0)
    return ''
  const grouped = new Map<number, string[]>()
  for (const t of times) {
    const list = grouped.get(t.day) ?? []
    list.push(t.period)
    grouped.set(t.day, list)
  }
  return Array.from(grouped.entries(), ([day, periods]) => `週${DAY_LABELS[day] ?? day} ${periods.join(',')}`)
    .join(' / ')
}

function mapCourseOutToCourse(raw: CourseOut): Course {
  return {
    id: raw.id,
    name: raw.title,
    teacher: raw.teachers.join('、'),
    tags: [raw.courseType === 'REQUIRED' ? '必修' : '選修', ...raw.departments],
    ratings: { reward: 0, score: 0, easiness: 0, teacherStyle: 0 },
    semester: raw.lastSemester ?? undefined,
    department: raw.departments.join('、'),
    code: raw.classNo,
    time: formatTimes(raw.times),
    credits: raw.credit,
    type: raw.courseType,
  }
}

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
    const raw = await request<CourseOut[]>(`/api/courses${suffix}`)
    return raw.map(mapCourseOutToCourse)
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
      const raw = await request<CourseOut>(`/api/courses/${courseId}`)
      return mapCourseOutToCourse(raw)
    }
    catch {
      return null
    }
  }
  return mockCourses.find(course => course.id === courseId) ?? null
}
