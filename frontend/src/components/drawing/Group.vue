<script setup>
const props = defineProps({
  x: {
    type: Number,
    default: 0,
  },
  y: {
    type: Number,
    default: 0,
  },
  width: {
    type: Number,
  },
  height: {
    type: Number,
  },
  fill: {
    type: String,
  },
  rx: {
    type: Number,
  },
  ry: {
    type: Number,
  },
  padding: {
    type: [String, Number, Array],
    default: 0,
  },
  gap: {
    type: [String, Number],
    default: 0,
  },
  direction: {
    type: String, // 'row' || 'col'
  },
  justify: {
    type: String, // 'start' || 'center' || 'end' || 'stretch' || 'between' || 'around'
  },
  align: {
    type: String, // 'start' || 'center' || 'end' || 'stretch'
  },
})

const self = ref(null)

const localPadding = $computed(() => {
  let padding = props.padding
  if (typeof padding === 'string')
    padding = padding.split(' ').map(e => +e)
  if (typeof padding === 'number')
    padding = [padding]
  if (padding?.length === 1)
    return Array(4).fill(padding[0])
  if (padding?.length === 2)
    return [padding[0], padding[1], padding[0], padding[1]]
  return padding ?? [0, 0, 0, 0]
})

const contentRect = ref({})

useResizeObserver(self, ([entry]) => {
  const target = entry?.target
  if (!target || typeof target.getBBox !== 'function')
    return

  const { x, y, width, height } = target.getBBox()
  const children = [...target.children].map((child) => {
    if (typeof child.getBBox === 'function') {
      const { x, y, width, height } = child.getBBox()
      return { x, y, width, height }
    }
    return { x: 0, y: 0, width: 0, height: 0 }
  })

  const { w: maxWidth, h: maxHeight } = children.reduce(
    (acc, { width, height }) => {
      if (width > acc.w)
        acc.w = width
      if (height > acc.h)
        acc.h = height
      return acc
    },
    { w: 0, h: 0 },
  )

  contentRect.value = {
    x,
    y,
    width,
    height,
    padding: localPadding,
    children,
    maxWidth,
    maxHeight,
  }
})

provide('parentRect', contentRect)
const notNull = num => (Number.isNaN(Number(num)) || num === null ? 0 : num)
</script>

<template>
  <g>
    <rect
      v-if="fill"
      :x="notNull(x)"
      :y="notNull(y)"
      :width="notNull(width)"
      :height="notNull(height)"
      :fill="fill"
      :rx="notNull(rx)"
      :ry="notNull(ry)"
    />
    <g ref="self">
      <slot />
    </g>
  </g>
</template>