<script setup>
import { ref } from 'vue'

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
  grow: {
    type: Boolean,
    default: false,
  },
  tooltip: {
    type: String,
  },
})

const bar = ref(null)
const { width } = useElementSize(bar)
</script>

<template>
  <div ref="bar" class="relative flex gap-2 items-center overflow-hidden">
    <div
      class="relative flex-1 overflow-hidden min-h-8 bg-gray/10 border-1 border--content/12 rounded-1"
      :class="{
        'h-8': !grow,
        'h-full': grow,
      }"
      :style="{ '--color': `var(--${color})` }"
    >
      <div
        class="absolute h-full px-2 gap-2 text-xs backdrop-filter-invert flex flex-nowrap items-center justify-between text--color"
        :style="{
          width: `${width}px`
        }"
      >
        <div v-if="label">{{ label }}</div>
        <div class="font-bold">{{ percentage.toFixed(2) }}%</div>
      </div>
      <div
        class="relative bg--color h-full tween overflow-hidden"
        :style="{
          width: `${percentage}%`,
        }"
      >
        <div
          class="absolute h-full px-2 gap-2 text-xs backdrop-filter-invert flex flex-nowrap items-center justify-between text-white"
          :style="{
            width: `${width}px`
          }"
        >
          <div v-if="label">{{ label }}</div>
          <div class="font-bold">{{ percentage.toFixed(2) }}%</div>
        </div>
      </div>
    </div>
    <QTooltip v-if="tooltip">{{ tooltip }}</QTooltip>
  </div>
</template>