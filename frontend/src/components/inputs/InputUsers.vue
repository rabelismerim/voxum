<script setup>
import { ref, computed, watch, toRef } from 'vue'

const props = defineProps({
  modelValue: {
    type: [Array, Object],
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
  valueKey: {
    type: String,
    default: 'id',
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
    :option-value="valueKey"
    emit-value
    map-options
    use-input
    fill-input
    input-debounce="0"
    multiple
    use-chips
    @filter="onFilter"
    @update:model-value="onInput"
  >
    <template #selected-item="scope">
      <div class="max-w-fill mt-1.5 mr-1.5 flex items-center no-wrap gap-2 rounded-full pl-1 pr-1 py-1 border-1 border--primary/12 whitespace-nowrap tween bg--primary/20 color-inherit">
        <div class="bg-transparent flex nowrap items-center flex-1 text-ellipsis overflow-hidden">
          <UserPicture :model-value="scope.opt" class="h-6 w-6 rounded-full mr-2" />
          <span class="whitespace-pre">{{ scope.opt?.fullName }}</span>
        </div>
        <div
          class="rounded-full bg-white/20 hover:bg-white/50 min-h-5 min-w-5 flex justify-center items-center cursor-pointer"
          @click="scope.removeAtIndex(scope.index)"
        >
          <div class="i-carbon-close" />
        </div>
      </div>
    </template>

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