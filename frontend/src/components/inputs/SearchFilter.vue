<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  search: {
    type: String,
    default: '',
  },
  field: {
    type: String,
    default: '',
  },
  options: {
    type: Object,
    default: () => ({}),
  },
  placeholder: {
    type: String,
    default: 'Buscar...',
  },
  tooltip: {
    type: String,
    default: '',
  },
  autoSize: {
    type: Boolean,
    default: false,
  },
  inputClass: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  grow: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:search', 'update:field', 'clear'])

const localSearch = ref(props.search)

watch(
  () => props.search,
  (newSearch) => {
    localSearch.value = newSearch
  }
)

const menuOptions = computed(() =>
  Object.entries(props.options).map(([value, label]) => ({ label, value }))
)

const input = ref(null)
const menu = ref(null)
const showMenu = ref(false)

onClickOutside(menu, () => (showMenu.value = false))

const clear = () => {
  localSearch.value = ''
  emit('update:search', '')
  emit('clear')
}

const updateSearch = () => emit('update:search', localSearch.value)

const updateField = async (value) => {
  showMenu.value = false
  emit('update:field', value)
  await delay?.(0.1)
  input.value?.focus()
}
</script>

<template>
  <div
    :class="[search ? 'outline--secondary' : 'focus-within:outline--primary', grow && 'w-full']"
    class="relative flex flex-nowrap rounded-1 h-9"
    @click.stop
  >
    <button
      v-if="Object.keys(options).length"
      type="button"
      class="relative bg--base pl-3 pr-2 border-y-1 border-l-1 rounded-l-1 border--content/12 flex flex-nowrap gap-2 items-center tween whitespace-nowrap"
      :class="{
        'bg--secondary text--base': search
      }"
      @click.stop="showMenu = !showMenu"
    >
      <div class="i-carbon-search" />
      <div>{{ options?.[field] ?? '' }}</div>
      <div
        class="i-carbon-chevron-down tween"
        :class="{ 'rotate-180': showMenu }"
      />
      <div
        v-show="showMenu"
        ref="menu"
        class="absolute text--content bottom-0 -right-1px w-[calc(100%+2px)] translate-y-100% z-100 shadow-2xl flex flex-col rounded-1 overflow-hidden bg--base border-1 border--content/12 min-w-[max-content]"
      >
        <button
          v-for="({ label, value }, index) in menuOptions"
          :key="index"
          type="button"
          class="hover:bg--primary/12 py-3 px-5 tween"
          :class="{ 'bg--primary/50!': value === field }"
          @click.stop="updateField(value)"
        >
          {{ label }}
        </button>
      </div>
    </button>
    <label
      class="inline-grid align-top items-center bg--base pl-2 pr-8.5 border-1 border--content/12 rounded-r-1"
      :class="{
        'w-full': !autoSize,
        'input-sizer max-w-[calc(var(--w)+3rem)]': autoSize,
        'rounded-l-1': !Object.keys(options).length,
      }"
      style="--w: 15rem;"
      :data-value="localSearch"
    >
      <input
        ref="input"
        v-model="localSearch"
        type="text"
        size="5"
        :placeholder="placeholder"
        class="outline-none py-1"
        :class="{
          'w-full': !autoSize,
          'max-w-[var(--w)]': autoSize,
          [inputClass]: inputClass,
        }"
        :disabled="disabled"
        @input="debounce ? debounce(updateSearch) : updateSearch()"
        @keyup.prevent
      >
    </label>
    <button
      v-if="localSearch?.length > 0"
      type="button"
      class="group absolute right-1 flex justify-center items-center top-1/2 -translate-y-1/2 h-7 w-7 rounded-1 hover:bg--error tween"
      @click="clear"
    >
      <div class="i-carbon-close text-lg group-hover:text-white" />
    </button>
    <Hint v-if="tooltip" :value="tooltip" />
  </div>
</template>

<style>
.input-sizer::after,
.input-sizer input {
  width: auto;
  min-width: 1em;
  grid-area: 1/2;
  font: inherit;
  margin: 0;
  resize: none;
}
.input-sizer::after {
  content: attr(data-value) " ";
  visibility: hidden;
  white-space: pre-wrap;
}
</style>