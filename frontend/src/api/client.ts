const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim() || ''

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

export function getDataSourceLabel(): 'API' {
  return 'API'
}

async function doFetch(path: string, options: RequestInit): Promise<Response> {
  return fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> | undefined),
    },
  })
}

export async function request<T>(path: string, options: RequestInit = {}, _isRetry = false): Promise<T> {
  if (!hasBackendApi()) {
    throw new ApiError('Backend API is not configured. Please set VITE_API_BASE_URL.', 500)
  }

  const response = await doFetch(path, options)

  if (response.status === 401 && !_isRetry && path !== '/api/v1/auth/refresh') {
    const refreshResponse = await doFetch('/api/v1/auth/refresh', { method: 'POST' })
    if (!refreshResponse.ok) {
      const { useAuthStore } = await import('@/stores/useAuthStore')
      useAuthStore().logout().catch(() => {
        // ignore logout errors in error handler
      })
      const { default: router } = await import('@/router')
      router.push({ name: 'login' })
      throw new ApiError('Session expired', 401)
    }
    return request<T>(path, options, true)
  }

  if (!response.ok) {
    if (response.status === 401) {
      const { useAuthStore } = await import('@/stores/useAuthStore')
      useAuthStore().logout().catch(() => {
        // ignore logout errors in error handler
      })
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
