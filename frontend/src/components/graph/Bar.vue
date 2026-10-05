<script setup>
const props = defineProps({
  percentage: {
    type: Number,
    default: 0,
  },
  color: {
    type: String,
    default: 'primary',
  },
  label: {
    type: String,
  },
})
</script>

<template>
  <div class="relative flex-1 overflow-hidden rounded-1 h-4 bg-gray/10" :style="{ '--color': `var(--${color})` }">
    <div v-if="label" class="absolute w-max left-2 top-1/2 -translate-y-1/2 text-xs backdrop-filter-invert text--color">
      {{ label }}
    </div>
    <div
      class="relative bg--color h-full tween overflow-hidden max-w-full" :style="{
        width: `${percentage * 100}%`,
      }"
    >
      <div v-if="label" class="absolute w-max left-2 top-1/2 -translate-y-1/2 text-xs backdrop-filter-invert text-white">
        {{ label }}
      </div>
    </div>
  </div>
</template>