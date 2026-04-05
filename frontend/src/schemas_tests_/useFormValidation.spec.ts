import { describe, expect, it } from 'vitest'
import { nextTick } from 'vue'
import { useFormValidation } from '@/composables/useFormValidation'
import { loginSchema } from '@/schemas'

describe('useFormValidation', () => {
  it('marks all fields touched on validateAll', () => {
    const { getFieldError, validateAll } = useFormValidation(
      loginSchema,
      {
        email: '',
        password: '',
      },
    )

    const valid = validateAll()
    expect(valid).toBe(false)
    expect(getFieldError('email')).toBe('請輸入電子信箱')
    expect(getFieldError('password')).toBe('請輸入密碼')
  })

  it('updates touched field errors in real time', async () => {
    const { form, getFieldError, isValid, touchField } = useFormValidation(
      loginSchema,
      {
        email: '',
        password: '',
      },
    )

    touchField('email')
    await nextTick()
    expect(getFieldError('email')).toBe('請輸入電子信箱')

    form.email = '111223333@cc.ncu.edu.tw'
    await nextTick()
    expect(getFieldError('email')).toBeUndefined()

    expect(isValid.value).toBe(false)
    form.password = 'secret'
    await nextTick()
    expect(isValid.value).toBe(true)
  })

  it('resets form state', async () => {
    const { form, getFieldError, isValid, resetForm, touchField } = useFormValidation(
      loginSchema,
      {
        email: '',
        password: '',
      },
    )

    touchField('email')
    form.email = '111223333@cc.ncu.edu.tw'
    form.password = 'secret'
    await nextTick()
    expect(isValid.value).toBe(true)

    resetForm()
    await nextTick()

    expect(form.email).toBe('')
    expect(form.password).toBe('')
    expect(getFieldError('email')).toBeUndefined()
    expect(isValid.value).toBe(false)
  })
})
