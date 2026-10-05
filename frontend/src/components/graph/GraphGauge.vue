<script setup>
import { computed } from 'vue'

const props = defineProps({
  values: {
    type: Array,
    default: () => [],
  },
  title: {
    type: String,
  },
  emptyLabel: {
    type: String,
    default: 'Sem dados disponíveis...',
  },
  tooltip: {
    type: String,
  },
  radius: {
    type: Number,
    default: 30,
  },
  strokeWidth: {
    type: Number,
    default: 8,
  },
  contentClass: {
    type: String,
    default: 'grid-cols-2',
  },
})

const rangeBetween = (start, end, count) => {
  if (count <= 0) return []
  const step = (end - start) / Math.max(count, 1)
  return Array.from({ length: count }, (_, i) => start + step * i)
}

const colors = computed(() => {
  const count = props.values.length
  if (count === 0) return []
  if (count === 1) return ['hsl(81, 68%, 44%)']
  return [...rangeBetween(44, 10, count - 1), 0].map(
    lighting => `hsl(81, 68%, ${lighting}%)`
  )
})

const mappedValues = computed(() =>
  props.values.reduce(
    (acc, { count = 0, label, color }) => {
      acc.items.push({
        label,
        color,
        count,
        start: acc.total,
      })
      acc.total += count
      return acc
    },
    { items: [], total: 0 }
  ).items
)

const strokeSize = computed(() => 2 * Math.PI * props.radius)
const total = computed(() => props.values.reduce((acc, { count = 0 }) => acc + count, 0))
const isAllNull = computed(() => props.values.every(({ count }) => !count))
</script>

<template>
  <div class="bg--base flex flex-col items-stretch gap-3 py-4 px-6 border-1 border--content/12 rounded-1">
    <div v-if="title" class="flex no-wrap gap-3 items-start font-bold text-xl">
      {{ title }}
      <Hint v-if="tooltip" :value="tooltip" class="mt-1.25" />
    </div>
    <div
      class="grid flex-1 items-center gap-6"
      :class="contentClass"
    >
      <div class="flex justify-center items-center">
        <svg
          :viewBox="`0 0 ${2 * radius + strokeWidth} ${2 * radius + strokeWidth}`"
          class="w-4/5"
        >
          <circle
            :cx="radius + strokeWidth / 2"
            :cy="radius + strokeWidth / 2"
            :r="radius"
            :stroke-width="strokeWidth"
            stroke="#DFDFDF"
            class="fill-none"
          />
          <g v-if="!isAllNull && total > 0">
            <circle
              v-for="(item, i) in mappedValues"
              :key="item.label || i"
              :cx="radius + strokeWidth / 2"
              :cy="radius + strokeWidth / 2"
              :r="radius"
              :stroke="item.color || colors[i]"
              :stroke-width="strokeWidth"
              class="fill-none origin-center -rotate-90"
              :style="{
                strokeDasharray: strokeSize,
                strokeDashoffset: (1 - item.count / total) * strokeSize,
                transform: `rotate(${(360 / total) * item.start - 90}deg)`,
              }"
            />
          </g>
          <g class="origin-center translate-x-1/2 translate-y-1/2">
            <text y="0" class="font-bold" text-anchor="middle">
              {{ total }}
            </text>
            <text y="10" class="text-xs" text-anchor="middle">
              Total
            </text>
          </g>
        </svg>
      </div>
      <div>
        <div v-if="values.length < 1">
          {{ emptyLabel }}
        </div>
        <div
          v-else
          class="grid gap-2 justify-center"
        >
          <div
            v-for="(item, i) in values"
            :key="item.label || i"
            class="flex items-center gap-2 no-wrap"
          >
            <div
              class="min-w-4 h-4 rounded-full"
              :style="{
                background: item.color || colors[i],
              }"
            />
            <div class="whitespace-pre text-xs">
              {{ item.label }}
              <span class="bg-gray-200 px-1 py-0.5 ml-1 rounded-1 font-bold text-xs">
                {{ item.count }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>