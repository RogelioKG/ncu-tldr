import { request } from './client'

export interface AuthUser {
  id: string
  email: string
  displayName: string
  isActive: boolean
  emailVerified: boolean
}

export interface AuthResult {
  accessToken: string
  tokenType: string
  user: AuthUser
}

export interface MessageResponse {
  message: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload extends LoginPayload {
  displayName: string
}

export async function login(payload: LoginPayload): Promise<AuthResult> {
  return await request<AuthResult>('/api/v1/auth/login', {
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

export async function getMe(token: string): Promise<AuthUser> {
  return await request<AuthUser>('/api/v1/auth/me', { token })
}
