<script setup>
import { ref, computed, watch, toRef } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  label: {
    type: String,
    default: 'CPF / CNPJ',
  },
  rules: {
    type: Array,
    default: () => [],
  },
  errorMessages: {
    type: Object,
    default: () => ({}),
  },
  errorKey: {
    type: String,
    default: '',
  },
  grow: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const isCPF = ref(true)
watch(
  () => props.modelValue,
  (val) => {
    isCPF.value = (val || '').toString().replace(/[^0-9]/g, '').length <= 11
  },
  { immediate: true }
)

const input = ref(null)
const hasError = computed(() => input.value?.hasError || false)
const { clearError } = useBackendErrors(toRef(props, 'errorMessages'))

function onInput(value) {
  if (props.errorKey) clearError(props.errorKey)
  emit('update:modelValue', value)
}

function onPaste(evt) {
  const clipBoardData = evt?.clipboardData?.getData('text') || ''
  const value = clipBoardData.replace(/[^0-9]/g, '')
  isCPF.value = value.length <= 11
  emit('update:modelValue', value)
}
</script>

<template>
  <QInput
    ref="input"
    :model-value="modelValue"
    :label="label"
    :maxlength="18"
    :mask="String(modelValue || '').length <= 14 && isCPF ? '###.###.###-###' : '##.###.###/####-##'"
    :rules="[
      ...rules,
      value => !value || value.length === 14 || value.length === 18 || 'Precisa ser um CPF ou um CNPJ',
      value => !value || value.length === 18 || (value.length === 14 && isValidCPF(value)) || 'CPF não é válido',
      value => !value || value.length === 14 || (value.length === 18 && isValidCNPJ(value)) || 'CNPJ não é válido',
    ]"
    :error="!!errorMessages[errorKey]"
    :error-message="errorMessages[errorKey] || ''"
    outlined
    :dense="!grow"
    @update:model-value="onInput"
    @paste.prevent="onPaste"
  />
</template>