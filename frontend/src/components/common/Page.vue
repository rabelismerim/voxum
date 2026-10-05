<script setup>
const props = defineProps({
  hideHorizontal: {
    type: Boolean,
    default: true,
  },
  hideVertical: {
    type: Boolean,
  },
  loading: {
    type: Boolean,
  },
})
</script>

<template>
  <div class="grid overflow-hidden h-full" style="grid-template-rows: minmax(0,auto) minmax(0,1fr) minmax(0, auto)">
    <div class="z-2 max-w-100vw">
      <QLinearProgress v-if="loading" indeterminate color="secondary" class="absolute z-100 h-1.5" />
      <slot name="top" />
    </div>
    <div class="grid overflow-hidden z-1 h-full max-h-full" style="grid-template-columns: minmax(0,auto) minmax(0,1fr) minmax(0,auto)">
      <div class="relative z-1 flex no-wrap overflow-y-hidden">
        <slot name="left" />
      </div>
      <div
        class="relative flex flex-col flex-1 h-full"
        :class="{
          'overflow-x-hidden': hideHorizontal,
          'overflow-y-hidden': hideVertical,
        }"
      >
        <div class="flex-1"/>
        <slot />
        <div class="flex-1"/>
      </div>
      <div class="relative z-1 flex no-wrap overflow-y-hidden">
        <slot name="right" />
      </div>
    </div>
    <div class="z-2 max-w-100vw">
      <slot name="bottom" />
    </div>
  </div>
</template>
