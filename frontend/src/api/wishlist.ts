import type { WishCourse } from '@/types'
import { mockWishList } from '@/mock/wishList'
import { hasBackendApi, request } from './client'

export interface AddWishPayload {
  name: string
  teacher: string
}

export async function getWishlist(): Promise<WishCourse[]> {
  if (hasBackendApi()) {
    return await request<WishCourse[]>('/wishlist')
  }
  return mockWishList.map(row => ({ ...row, voteCount: 1 }))
}

export async function addWish(payload: AddWishPayload, token?: string): Promise<WishCourse> {
  if (hasBackendApi()) {
    return await request<WishCourse>('/wishlist', {
      method: 'POST',
      body: JSON.stringify(payload),
      token,
    })
  }
  const existing = mockWishList.find(row => row.name === payload.name && row.teacher === payload.teacher)
  if (existing) {
    return { ...existing, voteCount: 2 }
  }
  const nextId = mockWishList.reduce((maxId, row) => Math.max(maxId, row.id), 0) + 1
  return {
    id: nextId,
    name: payload.name,
    teacher: payload.teacher,
    voteCount: 1,
  }
}

export async function removeWish(wishId: number, token?: string): Promise<void> {
  if (hasBackendApi()) {
    await request<void>(`/wishlist/${wishId}`, { method: 'DELETE', token })
  }
}
