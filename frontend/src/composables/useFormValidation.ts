import type { ZodIssue, ZodType } from 'zod'
import { computed, reactive, ref, watch } from 'vue'

/**
 * 表單驗證錯誤型別
 */
export type FormErrors<T> = Partial<Record<keyof T | '_form', string>>

/**
 * 欄位觸碰狀態型別
 */
export type FieldTouched<T> = Partial<Record<keyof T, boolean>>

/**
 * 通用表單驗證 Composable
 *
 * @param schema - Zod 驗證 schema
 * @param initialValues - 表單初始值
 * @returns 表單狀態與驗證方法
 *
 * @example
 * ```ts
 * const { form, errors, isValid, validateField, validateAll, resetForm } =
 *   useFormValidation(loginSchema, { email: '', password: '' })
 * ```
 */
export function useFormValidation<T extends Record<string, unknown>>(
  schema: ZodType<T>,
  initialValues: T,
) {
  const form = reactive({ ...initialValues }) as T
  const errors = reactive<FormErrors<T>>({})
  const touched = reactive<FieldTouched<T>>({})
  const isValid = ref(false)

  function getIssueKey(issue: ZodIssue): keyof T | '_form' {
    const firstPath = issue.path[0]
    if (firstPath === undefined || firstPath === '_form') {
      return '_form'
    }
    return String(firstPath) as keyof T
  }

  function buildIssueMap(issues: ZodIssue[]): Map<keyof T | '_form', string> {
    const issueMap = new Map<keyof T | '_form', string>()
    for (const issue of issues) {
      const key = getIssueKey(issue)
      if (!issueMap.has(key)) {
        issueMap.set(key, issue.message)
      }
    }
    return issueMap
  }

  function clearErrors() {
    for (const key of Object.keys(errors)) {
      delete errors[key as keyof FormErrors<T>]
    }
  }

  function validateAndSyncErrors(includeUntouchedFields: boolean): boolean {
    const result = schema.safeParse(form)
    isValid.value = result.success

    clearErrors()
    if (result.success) {
      return true
    }

    const issueMap = buildIssueMap(result.error.issues)
    const touchedKeys = new Set(Object.keys(touched) as Array<keyof T>)
    const visibleKeys = includeUntouchedFields
      ? new Set<keyof T | '_form'>([
          ...Object.keys(initialValues) as Array<keyof T>,
          '_form',
        ])
      : new Set<keyof T | '_form'>([
          ...touchedKeys,
          '_form',
        ])

    for (const [key, message] of issueMap.entries()) {
      if (visibleKeys.has(key)) {
        errors[key] = message
      }
    }

    return false
  }

  function validateField(field: keyof T): boolean {
    touched[field] = true
    validateAndSyncErrors(false)
    return !errors[field]
  }

  function validateAll(): boolean {
    for (const key of Object.keys(initialValues) as Array<keyof T>) {
      touched[key] = true
    }
    return validateAndSyncErrors(true)
  }

  /**
   * 重置表單到初始狀態
   */
  function resetForm() {
    Object.assign(form, initialValues)
    clearErrors()
    Object.keys(touched).forEach(key => delete touched[key as keyof T])
    isValid.value = false
  }

  /**
   * 標記欄位為已觸碰（用於 blur 事件）
   */
  function touchField(field: keyof T) {
    touched[field] = true
    validateAndSyncErrors(false)
  }

  /**
   * 取得欄位錯誤訊息（僅在欄位被觸碰後顯示）
   */
  function getFieldError(field: keyof T): string | undefined {
    return touched[field] ? errors[field] : undefined
  }

  /**
   * 檢查欄位是否有錯誤
   */
  const hasError = computed(() => (field: keyof T) => {
    return touched[field] && !!errors[field]
  })

  watch(
    form,
    () => {
      validateAndSyncErrors(false)
    },
    { deep: true, immediate: true },
  )

  return {
    form,
    errors,
    touched,
    isValid,
    validateField,
    validateAll,
    resetForm,
    touchField,
    getFieldError,
    hasError,
  }
}
