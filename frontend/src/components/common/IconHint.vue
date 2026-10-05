<script setup>
const props = defineProps({
  icon: {
    type: String,
    default: 'i-carbon-user',
  },
  tooltip: {
    type: String,
    default: '',
  },
  dark: {
    type: Boolean,
  },
})
const {isMobile} = useAmbient()
</script>

<template>
  <div
    class="h-7 w-7 p-1.5 rounded-full flex justify-center items-center"
    :class="{
      'bg-black': dark,
      'bg-white border-1 border-gray-6': !dark,
    }"
  >
    <div
      class="w-full h-full"
      :class="{
        [icon]: icon,
        'color-white': dark,
        'color-gray-6': !dark,
      }"
    />
    <QTooltip v-if="!isMobile()">
      <div class="whitespace-pre">
        {{ tooltip.replaceAll('\\n', '\n') }}
      </div>
    </QTooltip>
  </div>
</template>
