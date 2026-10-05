<script setup>
import { ref, computed, watch, toRef } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean, Object],
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
  options: {
    type: Array,
    default: () => [],
  },
  toAdd: {
    type: Function,
    default: null,
  },
  errorMessages: {
    type: Object,
    default: () => ({}),
  },
  errorKey: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'update:options'])

const select = ref(null)
const hasError = computed(() => select.value?.hasError || false)
const { clearError } = useBackendErrors(toRef(props, 'errorMessages'))

function onInput(value) {
  if (props.errorKey) clearError(props.errorKey)
  emit('update:modelValue', value)
}

const loading = ref(false)
const inputValue = ref('')
const filteredOptions = ref([...props.options])

watch(
  () => props.options,
  (newOptions) => {
    filteredOptions.value = newOptions
  }
)

async function addNewItem() {
  if (!inputValue.value) {
    throwError?.({
      message: 'Precisa de uma descrição para adicionar...',
    })
    return
  }
  loading.value = true
  try {
    if (props.toAdd) {
      const value = await props.toAdd(inputValue.value)
      emit('update:options', [...props.options, value])
      inputValue.value = ''
      select.value?.updateInputValue('', true)
      select.value?.add(value)
    }
  } catch (error) {
    console.error(`ERROR ON ADD ITEM TO LIST ${props.label?.toUpperCase() || ''}:`, error)
  } finally {
    loading.value = false
  }
}

function onFilter(val, update) {
  update(() => {
    inputValue.value = val
    filteredOptions.value = props.options
      .filter(Boolean)
      .filter(v => v?.description?.toLowerCase()?.includes(val?.toLowerCase()))
  })
}
</script>

<template>
  <QSelect
    ref="select"
    :model-value="modelValue"
    :loading="loading"
    :options="filteredOptions"
    :label="label"
    :rules="rules"
    :error="!!errorMessages[errorKey]"
    :error-message="errorMessages[errorKey] || ''"
    map-options
    option-value="id"
    option-label="description"
    outlined
    use-input
    hide-selected
    fill-input
    input-debounce="0"
    emit-value
    dense
    @filter="onFilter"
    @update:model-value="onInput"
  >
    <template #no-option>
      <Btn
        v-if="toAdd"
        :label="`Adicionar${label ? ` ${label}` : ''}`"
        class="w-full h-12 uppercase active:scale-100! active:shadow-none!"
        color="primary"
        icon="i-carbon-add-filled"
        @click="addNewItem"
      />
    </template>
  </QSelect>
</template>