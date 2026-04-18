import type { Course, CourseSummary, TimeSlot } from '@/types'
import { ApiError, request } from './client'

/** Shape returned by GET /api/v1/courses and GET /api/v1/courses/{id} */
interface RawRatings {
  gain: number
  highScore: number
  easiness: number
  teacherStyle: number
}

interface RawGradingItem {
  label: string
  percentage: number
}

interface RawSummary {
  overview: string
  targetAudience: string
  textbook: string
  prerequisites: string
  weeklyHours: string
  gradingItems: RawGradingItem[]
  notes: string
  reviewCount: number
}

interface RawCourse {
  id: number
  name: string
  teacher: string
  tags: string[]
  ratings: RawRatings
  semester: string | null
  department: string | null
  code: string | null
  time: string | null
  credits: number | null
  type: string | null
  summary: RawSummary | null
}

function normalizeRatings(raw: RawRatings) {
  return {
    gain: raw.gain,
    highScore: raw.highScore,
    easiness: raw.easiness,
    teacherStyle: raw.teacherStyle,
  }
}

function normalizeSummary(raw: RawSummary): CourseSummary {
  return {
    overview: raw.overview,
    targetAudience: raw.targetAudience,
    textbook: raw.textbook,
    prerequisites: raw.prerequisites,
    weeklyHours: raw.weeklyHours,
    gradingItems: raw.gradingItems,
    notes: raw.notes,
    reviewCount: raw.reviewCount,
  }
}

function normalizeApiCourse(raw: RawCourse): Course {
  return {
    id: raw.id,
    name: raw.name,
    teacher: raw.teacher,
    tags: raw.tags,
    ratings: normalizeRatings(raw.ratings),
    semester: raw.semester ?? undefined,
    department: raw.department ?? undefined,
    code: raw.code ?? undefined,
    time: raw.time ?? undefined,
    credits: raw.credits ?? undefined,
    type: raw.type ?? undefined,
    summary: raw.summary ? normalizeSummary(raw.summary) : undefined,
  }
}

export async function getCourses(params?: { q?: string, sort?: string, slots?: TimeSlot[] }): Promise<Course[]> {
  const query = new URLSearchParams()
  if (params?.q)
    query.set('q', params.q)
  if (params?.sort)
    query.set('sort', params.sort)
  params?.slots?.forEach(s => query.append('slots', `${s.day}_${s.period}`))
  const suffix = query.toString() ? `?${query.toString()}` : ''
  const raw = await request<RawCourse[]>(`/api/v1/courses${suffix}`)
  return raw.map(normalizeApiCourse)
}

export async function getCourseById(courseId: number): Promise<Course | null> {
  try {
    const raw = await request<RawCourse>(`/api/v1/courses/${courseId}`)
    return normalizeApiCourse(raw)
  }
  catch (err) {
    if (err instanceof ApiError && err.status === 404)
      return null
    throw err
  }
}
