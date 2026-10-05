<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  values: {
    type: Array,
    default: () => [],
  },
  title: {
    type: String,
  },
  tooltip: {
    type: String,
  },
  padding: {
    type: Number,
    default: 16,
  },
  gap: {
    type: Number,
    default: 8,
  },
  border: {
    type: Number,
    default: 1,
  },
})

const size = ref({ width: 0, height: 0 })

function onResize({ width, height }) {
  size.value.width = width
  size.value.height = height
}

const count = computed(() => props.values.length)

const axis = computed(() => ({
  top: 1,
  left: 1,
  width: Math.max(size.value.width - 2, 0),
  height: Math.max(size.value.height - 17, 0),
}))

const maxValue = computed(() =>
  props.values.reduce((acc, [, value]) => (value > acc ? value : acc), 0)
)

function getBar(value, index) {
  const max = maxValue.value || 1
  const chartHeight = Math.max(size.value.height - props.padding - 22, 0)
  const h = (value / max) * chartHeight
  const divisor = count.value > 1 ? count.value - 1 : 1
  return {
    y: size.value.height - h - 32,
    x: (size.value.width / divisor) * index,
  }
}

const bars = computed(() =>
  props.values.map(([label, value], index) => ({
    label,
    value,
    ...getBar(value, index),
  }))
)

const path = computed(() => {
  if (bars.value.length === 0) return ''
  const [{ x, y }, ...rest] = bars.value
  return `M${x},${y} L${rest.map(({ x, y }) => `${x},${y}`).join(' ')}`
})

const closePath = computed(() => {
  if (!path.value) return ''
  return `${path.value} L${axis.value.width},${axis.value.height - 16} L${axis.value.left},${axis.value.height - 16} Z`
})
</script>

<template>
  <div class="relative bg--base flex flex-col items-stretch gap-3 py-4 px-6 border-1 border--content/12 rounded-1 min-h-57">
    <div v-if="title" class="flex no-wrap gap-3 items-start font-bold text-xl">
      {{ title }}
      <Hint v-if="tooltip" :value="tooltip" class="mt-1.25" />
    </div>
    <div v-resize:0="onResize" class="flex-1 items-center">
      <div
        v-if="values.length < 1"
        class="flex items-center justify-center h-full"
      >
        Sem dados disponíveis...
      </div>
      <div v-else>
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1" :viewBox="`0 0 ${size.width} ${size.height}`">
          <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" class="stop--secondary/50" />
              <stop offset="100%" class="stop--secondary/0" />
            </linearGradient>
          </defs>
          <g :style="{ transform: `translateY(${padding}px)` }">
            <path :d="closePath" fill="url(#grad)" />
            <path :d="path" class="fill-none stroke-4 stroke--secondary" />
            <g v-for="({ label, value, x, y }, i) in bars" :key="i">
              <circle :cx="x" :cy="y" r="4" class="fill--secondary/60 stroke--secondary stroke-1" />
              <text :x="x" :y="size.height - 16">{{ label }}</text>
              <text v-if="value !== 0" :x="x" :y="y - 10">{{ value }}</text>
            </g>
          </g>
          <path stroke="#64748b" fill="none" stroke-width="2" :d="`M${axis.left} ${axis.top} v${axis.height}h${axis.width}`" />
        </svg>
      </div>
    </div>
  </div>
</template>