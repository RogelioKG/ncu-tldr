import { vi } from 'vitest'

vi.mock('@vueuse/integrations', () => ({
  useFocusTrap: vi.fn(() => ({
    activate: vi.fn(),
    deactivate: vi.fn(),
    hasFocus: { value: false },
    isPaused: { value: false },
    pause: vi.fn(),
    unpause: vi.fn(),
  })),
}))

vi.mock('@vueuse/integrations/useFocusTrap', () => ({
  useFocusTrap: vi.fn(() => ({
    activate: vi.fn(),
    deactivate: vi.fn(),
    hasFocus: { value: false },
    isPaused: { value: false },
    pause: vi.fn(),
    unpause: vi.fn(),
  })),
}))
