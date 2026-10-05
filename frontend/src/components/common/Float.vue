<script setup>
const floating = ref(null)

onMounted(async () => {
  // const position = await computePosition(btn.value.target, floating.value, {
  //   placement: 'bottom',
  //   middleware: [offset(8), flip(), shift({padding: 4})],
  // })
  // const {x, y} = position
  // Object.assign(floating.value.style, {
  //   left: `${x}px`,
  //   top: `${y}px`,
  // })
})
</script>

<template>
  <div ref="floating" class="absolute top-0 px-3 py-1 rounded-2 text--base bg--content/80 border-1 border--black/50 mr-4">
    <slot/>
  </div>
</template>