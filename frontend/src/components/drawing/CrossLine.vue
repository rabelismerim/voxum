<script setup>
const props = defineProps({
  x: {
    type: [Number, String],
  },
  y: {
    type: [Number, String],
  },
  color: {
    type: String,
    default: '#000',
  },
  width: {
    type: [Number, String],
    default: 1,
  },
  opacity: {
    type: [Number, String],
    default: 1,
  },
})

const notNull = num => (Number.isNaN(Number(num)) || num === null ? 0 : num)
const parentRect = inject('parentRect', ref({ width: 0, height: 0 }))
</script>

<template>
  <line
    v-if="x !== undefined"
    :x1="x"
    y1="0"
    :x2="x"
    :y2="parentRect.height"
    :stroke="color"
    :stroke-width="width"
    :opacity="opacity"
  />
  <line
    v-else-if="y !== undefined"
    x1="0"
    :y1="notNull(y)"
    :x2="notNull(parentRect.width)"
    :y2="notNull(y)"
    :stroke="color"
    :stroke-width="width"
    :opacity="opacity"
  />
</template>