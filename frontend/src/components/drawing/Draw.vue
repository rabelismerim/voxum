<script setup>
const props = defineProps({
  width: {
    type: [Number, String],
    default: 300,
  },
  height: {
    type: [Number, String],
    default: 150,
  },
  fill: {
    type: String,
  },
  camera: {
    type: Object,
  },
})

const self = ref(null)

const localCamera = $computed(() => ({
  x: props.camera?.x ?? 0,
  y: props.camera?.y ?? 0,
  width: props.camera?.width ?? props.width,
  height: props.camera?.height ?? props.height,
}))

const viewBox = $computed(
  () =>
    `${localCamera.x} ${localCamera.y} ${localCamera.width} ${localCamera.height}`,
)

const contentRect = ref({ x: 0, y: 0, width: 0, height: 0 })

useResizeObserver(self, ([entry]) => {
  if (entry?.target && typeof entry.target.getBBox === 'function') {
    const { x, y, width, height } = entry.target.getBBox()
    contentRect.value = { x, y, width, height }
  }
})

const notNull = num => (Number.isNaN(Number(num)) || num === null ? 0 : num)
provide('parentRect', contentRect)
</script>

<template>
  <svg ref="self" :viewBox="viewBox">
    <Rect
      v-if="fill"
      x="0"
      y="0"
      :width="notNull(width)"
      :height="notNull(height)"
      :color="fill"
    />
    <slot />
  </svg>
</template>