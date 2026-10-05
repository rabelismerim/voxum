<script setup>
import { ref, computed, nextTick, toRef } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
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
const { isMobile } = useAmbient()

const inputcontent = ref([])
const inputvalue = ref(null)
const input = ref(null)
const hasError = computed(() => input.value?.hasError || false)
const { clearError } = useBackendErrors(toRef(props, 'errorMessages'))

function clearErrors() {
  if (props.errorKey) clearError(props.errorKey)
}

function onInput(value) {
  clearErrors()
  emit('update:modelValue', value)
}

const inputValue = ref('')
const itemEditing = ref(-1)

async function editTag(index) {
  itemEditing.value = index
  await nextTick()
  if (inputcontent.value[0]) {
    inputcontent.value[0].focus()
  }
}

function add() {
  if (!inputValue.value) return
  clearErrors()
  const items = [...props.modelValue]
  items.push(inputValue.value)
  inputValue.value = ''
  emit('update:modelValue', items)
}

function remove(index) {
  clearErrors()
  const items = [...props.modelValue]
  items.splice(index, 1)
  emit('update:modelValue', items)
}

function clear() {
  clearErrors()
  emit('update:modelValue', [])
}

function updateItem(event, index) {
  clearErrors()
  const target = event.target
  const items = [...props.modelValue]
  items[index] = target?.value || ''
  emit('update:modelValue', items)
}

function onFocus() {
  nextTick(() => inputvalue.value?.focus())
}

function onBlur() {
  inputValue.value = ''
  itemEditing.value = -1
}

function getContentSize(textContent) {
  if (typeof document === 'undefined') return 0
  const div = document.createElement('span')
  div.innerText = textContent
  Object.assign(div.style, {
    whiteSpace: 'pre',
    visibility: 'hidden',
    position: 'absolute',
  })
  document.body.appendChild(div)
  const { width } = div.getBoundingClientRect()
  document.body.removeChild(div)
  return width
}
</script>

<template>
  <QField
    ref="input"
    :model-value="modelValue"
    :label="label"
    :rules="rules"
    :error="!!errorMessages[errorKey]"
    :error-message="errorMessages[errorKey] || ''"
    dense
    outlined
    tabindex="0"
    @update:model-value="onInput"
    @blur="onBlur"
    @focus="onFocus"
  >
    <template #control="{ id, floatingLabel }">
      <div class="flex gap-1 w-full pt-1.5 pb-1 pr-8">
        <div
          v-for="(item, index) in modelValue"
          :key="index"
          class="max-w-fill flex items-center no-wrap gap-2 rounded-full pl-3 pr-1 py-1 border-1 border--primary/12 whitespace-nowrap tween cursor-pointer"
          :class="{
            'bg--primary color-white': itemEditing === index,
            'bg--primary/20 color-inherit': itemEditing !== index,
          }"
          @click.stop="editTag(index)"
        >
          <input
            v-if="itemEditing === index"
            ref="inputcontent"
            :value="modelValue[index]"
            class="bg-transparent outline-none max-w-fill"
            :style="{
              width: `${getContentSize(modelValue[index])}px`,
            }"
            @input="updateItem($event, index)"
            @blur="itemEditing = -1"
          >
          <div
            v-else
            class="bg-transparent flex-1 text-ellipsis overflow-hidden"
          >
            <span class="whitespace-pre">{{ item }}</span>
          </div>
          <div
            class="rounded-full bg-white/20 hover:bg-white/50 min-h-5 min-w-5 flex justify-center items-center cursor-pointer"
            @click.stop="remove(index)"
          >
            <div class="i-carbon-close" />
          </div>
        </div>
        <input
          v-show="floatingLabel && itemEditing === -1"
          :id="id"
          ref="inputvalue"
          v-model="inputValue"
          class="bg-transparent outline-none flex-1 min-w-8"
          @keyup.enter="add"
          @focus="inputValue = ''; itemEditing = -1"
        >
      </div>
      <div class="group-hover:opacity-100 group-hover:pointer-events-auto absolute -right-.5 top-1/2 -translate-y-1/2">
        <div
          v-if="inputValue.length > 0"
          class="h-8 w-8 rounded-full bg--primary/80 hover:bg--primary flex justify-center items-center color-white text-lg cursor-pointer"
          @click.stop="add"
        >
          <div class="i-carbon-add" />
          <QTooltip v-if="!isMobile()">
            Adicionar novo item
          </QTooltip>
        </div>
        <div
          v-else-if="modelValue.length > 0"
          class="h-8 w-8 rounded-full bg-black/12 hover:bg--error hover:color-white flex justify-center items-center cursor-pointer tween"
          @dblclick.stop="clear"
        >
          <div class="i-carbon-trash-can" />
          <QTooltip v-if="!isMobile()">
            Para limpar todos os itens use um click duplo
          </QTooltip>
        </div>
      </div>
    </template>
  </QField>
</template>