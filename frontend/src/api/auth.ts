import { request } from './client'

export interface AuthUser {
  id: string
  email: string
  displayName: string
  isActive: boolean
  emailVerified: boolean
}

export interface MessageResponse {
  message: string
}

export interface LoginPayload {
  email: string
  password: string
  rememberMe?: boolean
}

export interface RegisterPayload {
  email: string
  password: string
  displayName: string
}

export async function login(payload: LoginPayload): Promise<AuthUser> {
  return await request<AuthUser>('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function register(payload: RegisterPayload): Promise<MessageResponse> {
  return await request<MessageResponse>('/api/v1/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function resendVerification(email: string): Promise<MessageResponse> {
  return await request<MessageResponse>('/api/v1/auth/resend-verification', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}

export async function getMe(): Promise<AuthUser> {
  return await request<AuthUser>('/api/v1/auth/me')
}

export async function logoutApi(): Promise<void> {
  await request<MessageResponse>('/api/v1/auth/logout', { method: 'POST' })
}
