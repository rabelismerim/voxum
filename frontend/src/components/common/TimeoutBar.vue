<script setup>
const props = defineProps({
  timeout: {
    type: Number,
    default: Number.POSITIVE_INFINITY,
  },
})

const bar = ref(null)

watchEffect(() => {
  if (bar.value === null)
    return
  if (props.timeout >= Number.POSITIVE_INFINITY)
    return
  bar.value.animate(
    [
      { transform: 'scaleX(100%)' },
      { transform: 'scaleX(0%)' },
    ],
    {
      duration: props.timeout * 1000,
    },
  )
})
</script>

<template>
  <div class="w-full h-1 rounded-1 bg-black/10 overflow-hidden">
    <div
      ref="bar"
      class="w-full h-full origin-left bg-white/60"
    />
  </div>
</template>
