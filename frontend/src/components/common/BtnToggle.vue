<script setup>
const props = defineProps({
  modelValue: {
    type: [String, Boolean, Number],
  },
  options: {
    type: Object,
    required: true,
  },
  grow: {
    type: Boolean,
  },
  disabled: {
    type: Boolean,
  }
})
const emit = defineEmits(['update:model-value'])
const items = $computed(() => Object.entries(props.options) ?? [])
</script>

<template>
  <div
    class="flex no-wrap border-1 rounded-1 overflow-hidden h-9"
    :class="{
      'w-full': grow,
      'border--primary': !disabled,
      'border--primary/40': disabled,
    }"
  >
    <Btn
      v-for="([value, label], index) in items"
      :key="index"
      :label="label"
      :transparent="modelValue !== value"
      :filled="modelValue === value"
      class="rounded-0 border-none"
      :class="{ 'flex-1': grow }"
      type="button"
      :disabled="disabled"
      @click="emit('update:model-value', value)"
    />
  </div>
</template>
