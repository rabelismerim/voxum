<script setup>
const props = defineProps({
  showButtons: {
    type: Boolean,
  },
  showScroll: {
    type: Boolean,
  },
  gap: {
    type: Number,
  },
})

const scroll = ref(null)
let current = $ref(0)
let position = $ref(0)
const { width: containerWidth } = useElementSize(scroll)
let scrollWidth = $ref(0)

function onScroll() {
  position = scroll.value?.scrollLeft
  scrollWidth = scroll.value?.scrollWidth
  const containerPositionX = scroll.value.getBoundingClientRect().x
  const positions = [...scroll.value.children]
    .map(el => Math.abs(el.getBoundingClientRect().x - containerPositionX))
  current = positions.reduce((acc, curr, index, arr) => curr < arr[acc] ? index : acc, 0)
}
function getElementPosition(index) {
  const positions = [...scroll.value.children]
    .map(el => el.offsetLeft)
  return positions[index]
}
function goTo(newPosition) {
  scroll.value.scrollLeft = newPosition
}
function goToNext() {
  goTo(getElementPosition(current + 1))
  current++
}
function goToBefore() {
  goTo(getElementPosition(current - 1))
  current--
}

onMounted(() => {
  onScroll()
})
</script>

<template>
  <div class="relative">
    <div
      ref="scroll"
      class="carousel pb-4 flex no-wrap overflow-x-scroll snap-x snap-mandatory gap-4 scroll-smooth"
      :class="{ 'hide-scrollbar': !showScroll }"
      @scroll="onScroll"
    >
      <slot />
    </div>
    <button
      v-if="position > 0"
      class="group absolute flex justify-center items-center top-50% -translate-y-50% -left-16 w-12 h-12 rounded-full border-1 border--content/12 bg--base "
      @click="goToBefore"
    >
      <div class="i-carbon-chevron-left text-2xl group-hover:color--secondary tween" />
      <div class="absolute inset-0 hover:bg--secondary/10 rounded-full tween" />
    </button>
    <button
      v-if="position < (scrollWidth - containerWidth)"
      class="group absolute flex justify-center items-center top-50% -translate-y-50% -right-16 w-12 h-12 rounded-full border-1 border--content/12 bg--base "
      @click="goToNext"
    >
      <div class="i-carbon-chevron-right text-2xl group-hover:color--secondary tween" />
      <div class="absolute inset-0 hover:bg--secondary/10 rounded-full tween" />
    </button>
  </div>
</template>

<style>
.carousel > * {
  scroll-snap-align: start;
}
</style>
