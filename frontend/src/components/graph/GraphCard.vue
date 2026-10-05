<script setup>
const props = defineProps({
  title: {
    type: String,
  },
  tooltip: {
    type: String,
  },
})
</script>

<template>
  <div class="bg--base flex flex-col items-stretch gap-2 md:gap-3 py-2 px-3 md:py-4 md:px-6 border-1 border--content/12 rounded-1">
    <div v-if="title" class="flex no-wrap gap-2 md:gap-3 items-start font-bold text-xl">
      {{ title }}
      <Hint v-if="tooltip" :value="tooltip" class="mt-1.25" />
    </div>
    <slot />
  </div>
</template>