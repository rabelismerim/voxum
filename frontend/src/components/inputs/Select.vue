<script setup>
import { ref, computed, watchEffect } from 'vue'

const props = defineProps({
  modelValue: {
    type: [Object, String, Number, Boolean],
    default: null,
  },
  labelKey: {
    type: String,
    default: 'label',
  },
  idKey: {
    type: String,
    default: 'id',
  },
  endpoint: {
    type: Object,
    default: null,
  },
  options: {
    type: Object,
    default: null,
  },
  listClasses: {
    type: String,
    default: 'min-w-10!',
  },
  emptyLabel: {
    type: String,
    default: 'Nenhum item encontrado',
  },
  itemsLabel: {
    type: String,
    default: 'items',
  },
  rules: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue'])

function getValueType(val) {
  return Object.prototype.toString.call(val).slice(8, -1)
}

function getItemAttr(item, key) {
  if (!item) return ''
  if (typeof item === 'object') return item[key] ?? ''
  return item
}

watchEffect(() => {
  const type = getValueType(props.modelValue)
  if (['Number', 'String', 'Boolean'].includes(type) && props.options && props.options[props.modelValue]) {
    emit('update:modelValue', {
      [props.idKey]: props.modelValue,
      [props.labelKey]: props.options[props.modelValue],
    })
  }
})

const localRules = computed(() =>
  props.rules?.map(rule => () => rule?.(props.modelValue)) ?? []
)

const use = computed(() => props.endpoint)

const searchBy = computed({
  get: () => use.value?.pagination?.value?.filterBy || '',
  set: filterBy => use.value?.updatePagination?.({ filterBy }),
})

const localOptions = computed(() => {
  if (props.options) {
    return Object.entries(props.options).map(([key, value]) => ({
      [props.idKey]: key,
      [props.labelKey]: value,
    }))
  }
  return use.value?.items?.value ?? []
})

const loading = computed(() => use.value?.loading?.value ?? false)
const onFirstPage = computed(() => use.value?.onFirstPage?.value ?? false)
const onLastPage = computed(() => use.value?.onLastPage?.value ?? false)
const page = computed(() => use.value?.pagination?.value?.page ?? 1)
const totalCount = computed(() => use.value?.pagination?.value?.rowsNumber ?? 0)
const pageCount = computed(() => Math.ceil(totalCount.value / (use.value?.pagination?.value?.rowsPerPage || 1)))

const loadOptions = () => {
  use.value?.updatePagination?.({ filterBy: '', page: 1 })
  use.value?.get?.()
}

const nextPage = () => props.endpoint?.nextPage?.()
const previousPage = () => props.endpoint?.previousPage?.()

const showMenu = ref(false)

const onOpenMenu = (value) => {
  showMenu.value = value
  if (value) loadOptions()
}

function chooseItem(item) {
  showMenu.value = false
  emit('update:modelValue', item)
}
</script>

<template>
  <QField
    outlined
    label="Outlined"
    stack-label
    dense
    class="select"
    :rules="localRules"
  >
    <template #control>
      <button class="text-left self-center w-full outline-none" tabindex="0" type="button">
        <div>{{ getItemAttr(modelValue, labelKey) }}</div>
      </button>
    </template>
    <template #append>
      <div class="text-4.5">
        <div
          class="i-carbon-chevron-down tween"
          :class="{ 'rotate-180': showMenu }"
        />
      </div>
    </template>
    <QMenu
      :model-value="showMenu"
      fit
      class="max-w-xl!"
      @update:model-value="onOpenMenu"
    >
      <QLinearProgress v-if="loading" indeterminate color="secondary" class="absolute z-100 h-1.5" />
      <div v-if="!options" class="sticky top-0 bg--base/50 backdrop-blur">
        <div class="flex p-2 flex-nowrap gap-2">
          <div class="flex flex-nowrap">
            <BtnIcon
              icon="i-carbon-chevron-left"
              outlined
              color="primary"
              tooltip="Página Anterior"
              class="rounded-r-0"
              :disabled="onFirstPage"
              @click="previousPage"
            />
            <BtnIcon
              icon="i-carbon-chevron-right"
              outlined
              color="primary"
              tooltip="Próxima Página"
              class="rounded-l-0 border-l-0"
              :disabled="onLastPage"
              @click="nextPage"
            />
          </div>
          <SearchFilter
            v-model:search="searchBy"
            hide-label
            class="flex-1"
          />
        </div>
        <div class="px-2 pb-1 text-3 flex gap-2 justify-between">
          <span>Página {{ page }} de {{ pageCount }}</span>
          <span>Total de {{ totalCount }} {{ itemsLabel }}</span>
        </div>
      </div>
      <QList
        v-if="localOptions?.length"
        :class="listClasses"
      >
        <template
          v-for="option in localOptions"
          :key="getItemAttr(option, idKey)"
        >
          <slot
            v-if="$slots.option"
            name="option"
            v-bind="{
              item: option,
              chooseItem: () => chooseItem(option)
            }"
          />
          <button
            v-else
            type="button"
            class="py-2.5 px-4 hover:bg--primary/12 w-full text-left"
            @click="chooseItem(option)"
          >
            {{ getItemAttr(option, labelKey) }}
          </button>
        </template>
      </QList>
      <div
        v-else
        class="pt-2.5 pb-4 px-4 text-center"
      >
        {{ emptyLabel }}
      </div>
    </QMenu>
  </QField>
</template>