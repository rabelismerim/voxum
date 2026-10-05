import { ref } from 'vue'

export default function useAccordion(initialState = false) {
  const isOpen = ref(initialState)

  const toggle = () => {
    isOpen.value = !isOpen.value
  }

  const open = () => {
    isOpen.value = true
  }

  const close = () => {
    isOpen.value = false
  }

  return {
    isOpen,
    toggle,
    open,
    close,
  }
}