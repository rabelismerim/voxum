<script setup>
const props = defineProps({
  title: {
    type: String,
    default: '',
  },
  subTitle: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div class="flex flex-col gap-2">
    <div v-if="$slots.top" class="flex">
      <slot name="top" />
    </div>
    <div class="flex justify-between gap-x-4 gap-y-2">
      <div class="flex no-wrap gap-2 items-center">
        <div v-if="$slots.title">
          <slot name="title" />
        </div>
        <div v-else class="flex items-center gap-4">
          <div>
            <h2 class="font-bold text-2xl md:text-4xl flex items-center text-balance">
              {{ title }}
            </h2>
            <div v-if="$slots.subtitle">
              <slot name="subtitle" />
            </div>
            <h3 v-else-if="subTitle" class="leading-5 mt-2">
              {{ subTitle }}
            </h3>
          </div>
          <slot name="side" />
        </div>
        <slot name="right" />
      </div>
      <div v-if="$slots.default" class="flex items-center gap-2">
        <slot />
      </div>
    </div>
    <div v-if="$slots.bottom" class="flex">
      <slot name="bottom" />
    </div>
  </div>
</template>
