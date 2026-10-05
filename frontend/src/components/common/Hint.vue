<script setup>
const props = defineProps({
  tooltip: {
    type: String,
  },
})
const {isMobile} = useAmbient()
</script>

<template>
  <div v-if="tooltip" class="cursor-help text-base inline-block">
    <div class="i-carbon-help-filled color-black/30 hover:color--primary tween" />
    <QTooltip v-if="!isMobile()">
      <div class="whitespace-pre">
        {{ tooltip.replaceAll('\\n', '\n') }}
      </div>
    </QTooltip>
  </div>
</template>
