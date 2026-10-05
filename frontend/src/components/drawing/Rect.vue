<script setup>
const props = defineProps({
  x: {
    type: [Number, String],
    default: 0,
  },
  y: {
    type: [Number, String],
    default: 0,
  },
  width: {
    type: [Number, String],
    default: 0,
  },
  height: {
    type: [Number, String],
    default: 0,
  },
  color: {
    type: String,
  },
  rx: {
    type: Number,
  },
  ry: {
    type: Number,
  },
  border: {
    type: String,
    default: '#000',
  },
  borderWidth: {
    type: [Number, String],
    default: 0,
  },
  borderOpacity: {
    type: [Number, String],
    default: 1,
  },
})

const notNull = num => (Number.isNaN(Number(num)) || num === null ? 0 : num)
</script>

<template>
  <rect
    :x="x"
    :y="y"
    :width="notNull(width)"
    :height="notNull(height)"
    :fill="color"
    :rx="notNull(rx)"
    :ry="notNull(ry)"
    :stroke="border"
    :stroke-width="notNull(borderWidth)"
    :stroke-opacity="notNull(borderOpacity)"
  />
</template>