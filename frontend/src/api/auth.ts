import { hasBackendApi, request } from './client'

export interface AuthUser {
  id: number
  email: string
  displayName: string
  isActive: boolean
}

export interface AuthResult {
  accessToken: string
  tokenType: string
  user: AuthUser
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload extends LoginPayload {
  displayName: string
}

const mockUsers = new Map<string, { id: number, password: string, displayName: string }>([
  ['demo@cc.ncu.edu.tw', { id: 1, password: 'password123', displayName: 'Demo User' }],
])

export async function login(payload: LoginPayload): Promise<AuthResult> {
  if (hasBackendApi()) {
    return await request<AuthResult>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  const row = mockUsers.get(payload.email)
  if (!row || row.password !== payload.password) {
    throw new Error('Invalid email or password')
  }
  return {
    accessToken: `mock-${crypto.randomUUID()}`,
    tokenType: 'bearer',
    user: {
      id: row.id,
      email: payload.email,
      displayName: row.displayName,
      isActive: true,
    },
  }
}

export async function register(payload: RegisterPayload): Promise<AuthResult> {
  if (hasBackendApi()) {
    return await request<AuthResult>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  if (mockUsers.has(payload.email)) {
    throw new Error('Email already registered')
  }
  const nextId = Math.max(...Array.from(mockUsers.values(), row => row.id), 0) + 1
  mockUsers.set(payload.email, {
    id: nextId,
    password: payload.password,
    displayName: payload.displayName,
  })
  return {
    accessToken: `mock-${crypto.randomUUID()}`,
    tokenType: 'bearer',
    user: {
      id: nextId,
      email: payload.email,
      displayName: payload.displayName,
      isActive: true,
    },
  }
}

export async function getMe(token: string): Promise<AuthUser> {
  if (hasBackendApi()) {
    return await request<AuthUser>('/api/auth/me', { token })
  }
  const email = [...mockUsers.keys()][0]
  const row = mockUsers.get(email)!
  return {
    id: row.id,
    email,
    displayName: row.displayName,
    isActive: true,
  }
}
