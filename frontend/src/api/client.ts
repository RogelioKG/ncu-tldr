/** 由 frontend/.env 或 .env.local 設定 VITE_API_BASE_URL，見 .env.example */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim() || ''

interface RequestOptions extends RequestInit {
  token?: string
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export function hasBackendApi(): boolean {
  return API_BASE_URL.length > 0
}

/** 正式流程固定由後端 API（DB/ORM）提供資料。 */
export function getDataSourceLabel(): 'API' {
  return 'API'
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  if (!hasBackendApi()) {
    throw new ApiError('Backend API is not configured. Please set VITE_API_BASE_URL.', 500)
  }

  const headers = new Headers(options.headers)
  headers.set('Content-Type', 'application/json')
  if (options.token) {
    headers.set('Authorization', `Bearer ${options.token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })
  if (!response.ok) {
    if (response.status === 401) {
      const { useAuthStore } = await import('@/stores/useAuthStore')
      useAuthStore().logout()
      const { default: router } = await import('@/router')
      router.push({ name: 'login' })
      throw new ApiError('Session expired', 401)
    }
    let message = `Request failed with status ${response.status}`
    try {
      const data = await response.json() as { detail?: string }
      if (data.detail) {
        message = data.detail
      }
    }
    catch {
      // ignore json parse errors
    }
    throw new ApiError(message, response.status)
  }

  if (response.status === 204) {
    return undefined as T
  }
  return await response.json() as T
}
