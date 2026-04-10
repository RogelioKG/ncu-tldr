import type { WishCourse } from '@/types'
import { request } from './client'

export interface AddWishPayload {
  name: string
  teacher: string
}

export async function getWishlist(): Promise<WishCourse[]> {
  return await request<WishCourse[]>('/api/v1/wishlist')
}

export async function addWish(payload: AddWishPayload, token?: string): Promise<WishCourse> {
  return await request<WishCourse>('/api/v1/wishlist', {
    method: 'POST',
    body: JSON.stringify(payload),
    token,
  })
}

export async function removeWish(wishId: number, token?: string): Promise<void> {
  await request<void>(`/api/v1/wishlist/${wishId}`, { method: 'DELETE', token })
}
