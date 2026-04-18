/**
 * 課程相關型別定義
 */

/**
 * 表單相關型別（從 Zod schema 推導）
 * 這些型別由 @/schemas 統一管理，確保前後端驗證一致性
 */
export type {
  CourseReviewInput,
  LoginInput,
  RegisterInput,
  WishFormInput,
} from '@/schemas'

export interface CourseRatings {
  /** 收穫評分 (0-5) */
  gain: number
  /** 分數評分 (0-5) */
  highScore: number
  /** 輕鬆程度評分 (0-5) */
  easiness: number
  /** 教師風格評分 (0-5) */
  teacherStyle: number
}

export interface GradingItem {
  /** 配分名稱 (e.g. 作業、期中、期末) */
  label: string
  /** 佔比百分比 (0-100) */
  percentage: number
}

export interface CourseSummary {
  /** 課程概述 */
  overview: string
  /** 適合族群 */
  targetAudience: string
  /** 上課用書 */
  textbook: string
  /** 建議先備知識 */
  prerequisites: string
  /** 平均每週額外投入時間 */
  weeklyHours: string
  /** 配分方式（結構化） */
  gradingItems: GradingItem[]
  /** 常見雷點或注意事項 */
  notes: string
  /** AI 統整參考的評價數量 */
  reviewCount: number
}

export interface CourseComment {
  id: number
  user: string
  /** 留言標題 / 一句話摘要 */
  title: string
  /** 留言內文 */
  content: string
  date: string
  /** 按讚數 */
  likes: number
  /** 倒讚數 */
  dislikes: number
  /** 回覆對象 ID（undefined/null = 根留言） */
  parentId?: number
  /** 評分資訊（可選，用於本地即時重算） */
  ratings?: CourseRatings
}

export interface CommentTreeNode {
  root: CourseComment
  replies: CourseComment[]
}

export { buildCommentTree } from '@/utils/commentTree'

export interface Course {
  /** 課程唯一識別碼 */
  id: number
  /** 課程名稱 */
  name: string
  /** 授課教師 */
  teacher: string
  /** 課程標籤 */
  tags: string[]
  /** 各項評分（無評價資料時為 undefined） */
  ratings?: CourseRatings

  /** 開課學期 (Optional for mock) */
  semester?: string
  /** 系所/單位 (Optional for mock) */
  department?: string
  /** 課號 (Optional for mock) */
  code?: string
  /** 上課時間 (Optional for mock) */
  time?: string
  /** 學分數 (Optional for mock) */
  credits?: number
  /** 必修/選修 (Optional for mock) */
  type?: string
  /**  (Optional for mock) */
  summary?: CourseSummary
  /** 匿名留言串 (Optional for mock) */
  comments?: CourseComment[]
}

export interface WishCourse {
  /** 課程唯一識別碼 (courses.id) */
  courseId: number
  /** 課程名稱 */
  title: string
  /** 票數（即有多少人投票） */
  voteCount: number
  /** 當前登入者是否已投票 */
  hasVoted: boolean
}

/** 單一時段選取 */
export interface TimeSlot {
  day: number
  period: string
}

/** 排序方向 */
export type SortDirection = 'desc' | 'asc'

/** 可排序欄位（評分 key 或綜合平均） */
export type SortableRatingField = keyof CourseRatings | 'overall'

/** 單一排序條件 */
export interface SortCriterion {
  /** 排序欄位（CourseRatings 的 key 或 'overall' 綜合平均） */
  field: SortableRatingField
  /** 顯示名稱 */
  label: string
  /** 排序方向 */
  direction: SortDirection
  /** 是否啟用 */
  enabled: boolean
}
