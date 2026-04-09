import type { Course } from '@/types'
import { ApiError, request } from './client'

/** Raw shape returned by the backend API */
interface RawCourseTime {
  day: number
  period: string
}

interface RawCourse {
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
  times: RawCourseTime[]
}

const DAY_LABELS = ['', '一', '二', '三', '四', '五', '六', '日']

function formatTimes(times: RawCourseTime[]): string {
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

function normalizeApiCourse(raw: RawCourse): Course {
  return {
    id: raw.id,
    name: raw.title,
    teacher: raw.teachers.join('、'),
    tags: [raw.courseType === 'REQUIRED' ? '必修' : '選修', ...raw.departments],
    semester: raw.lastSemester ?? undefined,
    department: raw.departments.join('、'),
    code: raw.classNo,
    time: formatTimes(raw.times),
    credits: raw.credit,
    type: raw.courseType,
  }
}

export async function getCourses(params?: { q?: string, sort?: string }): Promise<Course[]> {
  const query = new URLSearchParams()
  if (params?.q) {
    query.set('q', params.q)
  }
  if (params?.sort) {
    query.set('sort', params.sort)
  }
  const suffix = query.toString() ? `?${query.toString()}` : ''
  const raw = await request<RawCourse[]>(`/api/courses${suffix}`)
  return raw.map(normalizeApiCourse)
}

export async function getCourseById(courseId: number): Promise<Course | null> {
  try {
    const raw = await request<RawCourse>(`/api/courses/${courseId}`)
    return normalizeApiCourse(raw)
  }
  catch (err) {
    if (err instanceof ApiError && err.status === 404)
      return null
    throw err
  }
}
