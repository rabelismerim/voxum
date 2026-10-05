<script setup>
import { ref, computed, watch, toRef } from 'vue'

const props = defineProps({
  modelValue: {
    type: [Object, String, Number],
    required: true,
  },
  label: {
    type: String,
    default: '',
  },
  rules: {
    type: Array,
    default: () => [],
  },
  users: {
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
})

const emit = defineEmits(['update:modelValue'])

const input = ref(null)
const hasError = computed(() => input.value?.hasError || false)
const { clearError } = useBackendErrors(toRef(props, 'errorMessages'))

const options = ref([...props.users])

watch(
  () => props.users,
  (newUsers) => {
    options.value = newUsers
  }
)

function onInput(value) {
  if (props.errorKey) clearError(props.errorKey)
  emit('update:modelValue', value)
}

function onFilter(val, update) {
  update(() => {
    const needle = val.toLowerCase()
    options.value = props.users.filter(({ fullName }) =>
      fullName?.toLowerCase()?.includes(needle)
    )
  })
}
</script>

<template>
  <QSelect
    ref="input"
    :model-value="modelValue"
    :options="options"
    :label="label"
    :rules="rules"
    :error="!!errorMessages[errorKey]"
    :error-message="errorMessages[errorKey] || ''"
    outlined
    option-label="fullName"
    option-value="id"
    emit-value
    map-options
    use-input
    hide-selected
    fill-input
    input-debounce="0"
    dense
    @filter="onFilter"
    @update:model-value="onInput"
  >
    <template #option="scope">
      <QItem v-bind="scope.itemProps">
        <UserCell v-model="scope.opt" />
      </QItem>
    </template>

    <template #no-option>
      <QItem>
        <QItemSection class="text-grey">
          Não existe este usuário
        </QItemSection>
      </QItem>
    </template>
  </QSelect>
</template>