<script setup>
import { ref, computed, toRef } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
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
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:model-value', 'paste'])

const input = ref(null)
const hasError = computed(() => input.value?.hasError || false)
const { clearError } = useBackendErrors(toRef(props, 'errorMessages'))

const dateData = computed({
  get: () => {
    if (!props.modelValue) return {}
    const [year, month, day] = props.modelValue.slice(0, 10).split('-')
    return { day, month, year }
  },
  set: (value) => {
    const { day, month, year } = value || {}
    const newDate = (day && month && year) ? [year, month, day].join('-') : ''
    if (props.errorKey) clearError(props.errorKey)
    emit('update:model-value', newDate)
  },
})

const formatedDate = computed({
  get: () => {
    if (!dateData.value) return ''
    const { day, month, year } = dateData.value
    return [day, month, year].filter(Boolean).join('/')
  },
  set: (value) => {
    if (!value) {
      dateData.value = { day: '', month: '', year: '' }
      return
    }
    if (value.match(/\d{4}-\d{2}-\d{2}.*/)) {
      const [year, month, day] = value.slice(0, 10).split('-')
      dateData.value = { day, month, year }
      return
    }
    const [day, month, year] = value.split('/')
    dateData.value = { day, month, year }
  },
})
</script>

<template>
  <QInput
    ref="input"
    v-model="formatedDate"
    :label="label"
    :rules="rules"
    :error="!!errorMessages[errorKey]"
    :error-message="errorMessages[errorKey] || ''"
    outlined
    mask="##/##/####"
    dense
    :disable="disabled"
    @paste="emit('paste', $event)"
  >
    <template #append>
      <div class="i-carbon-calendar cursor-pointer">
        <QPopupProxy cover transition-show="scale" transition-hide="scale">
          <QDate
            :model-value="formatedDate"
            mask="DD/MM/YYYY"
            @update:model-value="value => emit('update:model-value', formatDateToBackend(value))"
          >
            <div class="row items-center justify-end">
              <Btn v-close-popup label="Fechar" color="primary" flat />
            </div>
          </QDate>
        </QPopupProxy>
      </div>
    </template>
  </QInput>
</template>