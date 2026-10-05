import { ref, watchEffect } from 'vue'

const isDark = ref(false)

export default function useDark() {
  const toggleDark = () => {
    isDark.value = !isDark.value
  }

  watchEffect(() => {
    if (typeof document !== 'undefined') {
      if (isDark.value) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  })

  return {
    isDark,
    toggleDark,
  }
}