<script setup>
const props = defineProps({
  modelValue: {
    type: [String, Number],
    required: true,
  },
  items: {
    type: Array,
    required: true,
  },
  search: {
    type: String,
  },
})
const emit = defineEmits(['update:model-value', 'update:search'])
</script>

<template>
  <div class="mb-4 border-b-2 border--content/12 flex justify-between items-center">
    <QTabs
      :model-value="modelValue"
      align="left"
      active-color="primary"
      class="max-w-full"
      @update:model-value="value => emit('update:model-value', value)"
    >
      <QTab
        v-for="(tab, index) in items"
        :key="index"
        :name="tab.value"
        :label="tab.label"
      />
    </QTabs>
    <div v-if="$slots.default">
      <slot />
    </div>
    <SearchFilter
      v-else-if="search !== undefined"
      :model-value="search"
      @update:model-value="value => emit('update:search', value)"
    />
  </div>
</template>
