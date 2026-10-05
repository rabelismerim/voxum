<script setup>
import { ref, computed, watch, toRef } from 'vue'

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
  min: {
    type: String,
    default: '',
  },
  max: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:model-value', 'paste'])

const input = ref(null)
const hasError = computed(() => input.value?.hasError || false)
const { clearError } = useBackendErrors(toRef(props, 'errorMessages'))

const minDate = computed(() => props.min?.slice(0, 10)?.replaceAll('-', '/') || '')
const maxDate = computed(() => props.max?.slice(0, 10)?.replaceAll('-', '/') || '')

const dateTimePattern = '##/##/#### ##:##'

const localDate = ref('')

watch(
  () => props.modelValue,
  (newVal) => {
    localDate.value = fromISOString(newVal)
  },
  { immediate: true }
)

const date = computed({
  get() {
    return localDate.value
  },
  set(newValue) {
    localDate.value = newValue
    if (!newValue) {
      emit('update:model-value', '')
      return
    }
    if (matchesPattern(newValue, dateTimePattern) && isValidDateTime(newValue)) {
      emit('update:model-value', toISOString(localDate.value))
    }
  },
})

function matchesPattern(value = '', pattern = '') {
  return pattern.split('').every((char, index) => {
    if (char === '#') return !!value.at(index)?.match(/\d/)
    return value.at(index) === char
  })
}

function toPattern(value = '', pattern = '') {
  const content = value.split('').filter(char => char.match(/\d/))
  let lastIndex = 0
  return pattern
    .split('')
    .map((char) => {
      if (lastIndex > content.length - 1) return undefined
      if (char !== '#') return char
      return content[lastIndex++]
    })
    .filter(Boolean)
    .join('')
}

function padStart(num, count = 2) {
  return (+num || 0).toString().padStart(count, '0')
}

function isValidDate(value = '') {
  value = value?.toString() ?? ''
  const [day, month, year] = value.split('/')
  if (+month === 2 && +day > 29) return false
  const isValidDay = +day > 0 && +day <= 31
  const isValidMonth = +month > 0 && +month <= 12
  const isValidYear = +year > 100
  return isValidDay && isValidMonth && isValidYear
}

function isValidTime(value = '') {
  value = value?.toString() ?? ''
  const [hours, minutes] = value.split(':')
  const isValidHours = +hours >= 0 && +hours < 24
  const isValidMinutes = +minutes >= 0 && +minutes < 60
  return isValidHours && isValidMinutes
}

function isValidDateTime(value = '') {
  value = value?.toString() ?? ''
  const [datePart, timePart] = value.split(' ')
  return isValidDate(datePart) && isValidTime(timePart)
}

function fromISOString(string) {
  if (!string) return ''
  const newDate = new Date(string)
  if (Number.isNaN(newDate.getTime())) return ''
  const day = newDate.getDate()
  const month = newDate.getMonth() + 1
  const year = newDate.getFullYear()
  const hours = newDate.getHours()
  const minutes = newDate.getMinutes()
  const content = padStart(day) + padStart(month) + padStart(year, 4) + padStart(hours) + padStart(minutes)
  return toPattern(content, dateTimePattern)
}

function toISOString(string) {
  if (!matchesPattern(string, dateTimePattern) || !isValidDateTime(string)) return ''
  const [day, month, year, hour, minutes] = string.split(/\/|\s|:/)
  const formatted = `${padStart(year, 4)}/${padStart(month)}/${padStart(+day)} ${padStart(+hour)}:${padStart(+minutes)}`
  return (new Date(formatted)).toISOString()
}
</script>

<template>
  <div>
    <QInput
      ref="input"
      v-model="date"
      outlined
      mask="##/##/#### ##:##"
      :label="label"
      :rules="[
        (value) => !value || matchesPattern(value, dateTimePattern) || 'Precisa preencher o padrão ##/##/#### ##:##',
        (value) => !value || isValidDateTime(value) || 'Precisa ser uma data válida e hora válida!',
        () => (!min || modelValue >= min) || `Precisa ser maior que ${fromISOString(min)}`,
        () => (!max || modelValue <= max) || `Precisa ser menor que ${fromISOString(max)}`,
        ...rules,
      ]"
      :error="!!errorMessages[errorKey]"
      :error-message="errorMessages[errorKey] || ''"
      :disable="disabled"
      dense
      @paste="emit('paste', $event)"
      @update:model-value="props.errorKey && clearError(props.errorKey)"
    >
      <template #prepend>
        <QIcon name="o_event" class="cursor-pointer">
          <QPopupProxy cover transition-show="scale" transition-hide="scale">
            <QDate
              v-model="date"
              mask="DD/MM/YYYY HH:mm"
              :options="d => (minDate ? d >= minDate : true) && (maxDate ? d <= maxDate : true)"
            >
              <div class="row items-center justify-end">
                <Btn label="Fechar" transparent class="uppercase" v-close-popup />
              </div>
            </QDate>
          </QPopupProxy>
        </QIcon>
      </template>
      <template #append>
        <QIcon name="o_access_time" class="cursor-pointer">
          <QPopupProxy cover transition-show="scale" transition-hide="scale">
            <QTime v-model="date" mask="DD/MM/YYYY HH:mm" format24h>
              <div class="row items-center justify-end">
                <Btn label="Fechar" transparent class="uppercase" v-close-popup />
              </div>
            </QTime>
          </QPopupProxy>
        </QIcon>
      </template>
    </QInput>
  </div>
</template>