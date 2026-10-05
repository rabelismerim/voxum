<script setup>
import { ref, computed, toRef } from 'vue'

const props = defineProps({
  modelValue: {
    type: Number,
    default: null,
  },
  label: {
    type: String,
    default: '',
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

const input = ref(null)
const hasError = computed(() => input.value?.hasError || false)
const { clearError } = useBackendErrors(toRef(props, 'errorMessages'))

function onInput(value) {
  if (props.errorKey) clearError(props.errorKey)
  emit('update:modelValue', value !== '' && value !== null ? Number(value) : null)
}
</script>

<template>
  <QInput
    ref="input"
    :model-value="modelValue"
    :label="label"
    :rules="rules"
    :error="!!errorMessages[errorKey]"
    :error-message="errorMessages[errorKey] || ''"
    outlined
    :dense="!grow"
    type="number"
    @update:model-value="onInput"
  />
</template>