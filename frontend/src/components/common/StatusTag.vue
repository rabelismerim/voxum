<script setup lang="ts">
const props = defineProps({
  label: {
    type: String,
  },
  color: {
    type: String,
    default: '#007db3',
  },
  tooltip: {
    type: String,
  },
})

const emit = defineEmits(['click'])
const {isMobile} = useAmbient()
</script>

<template>
  <div
    class="py-.5 pl-2 rounded-full flex no-wrap items-center font-normal color-black text-3.25 text--content"
    :class="tooltip ? 'cursor-help' : ''"
    :style="{
      background: `${color}20`,
      border: `1px solid ${color}20`,
    }"
    @click="emit('click', $event)"
  >
    <div class="flex-1">
      {{ label }}
    </div>
    <div
      class="h-3 w-3 rounded-full mr-1.5 ml-1"
      :style="{
        background: color,
      }"
    />
    <QTooltip v-if="tooltip && !isMobile()">
      {{ tooltip }}
    </QTooltip>
  </div>
</template>
