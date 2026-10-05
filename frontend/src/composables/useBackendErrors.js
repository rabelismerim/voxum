import { ref, unref } from 'vue'

export default function useBackendErrors(errorSource = ref({})) {
  const errors = errorSource
  const currentErrors = () => unref(errors) ?? {}

  const setErrors = (backendErrors) => {
    if (!backendErrors) {
      errors.value = {}
      return
    }

    if (typeof backendErrors === 'object') {
      errors.value = backendErrors
    }
  }

  const clearError = (field) => {
    const current = currentErrors()
    if (current && typeof current === 'object')
      delete current[field]
  }

  const clearErrors = () => {
    errors.value = {}
  }

  const getError = (field) => {
    return currentErrors()[field] || ''
  }

  return {
    errors,
    setErrors,
    clearError,
    clearErrors,
    getError,
  }
}