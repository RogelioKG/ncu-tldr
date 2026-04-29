import { ref } from 'vue'

export function useErrorToast() {
  const visible = ref(false)
  const title = ref<string | undefined>()
  const message = ref<string | undefined>()

  function show(t?: string, m?: string) {
    title.value = t
    message.value = m
    visible.value = true
  }

  function close() {
    visible.value = false
  }

  return { close, message, show, title, visible }
}
