<script setup>
import { computed } from 'vue'
import useAmbient from '../../composables/useambient'

const props = defineProps({
  src: {
    type: String,
    default: '',
  },
  alt: {
    type: String,
    default: '',
  },
  width: {
    type: Number,
  },
  height: {
    type: Number,
  },
  errorImage: {
    type: String,
    default: '',
  },
})
const image = ref(null)
const fallbackImage = computed(() => props.errorImage || `${useAmbient().baseUrl}/fallback/image.svg`)

function onError() {
  if (image.value && image.value.src !== fallbackImage.value)
    image.value.src = fallbackImage.value
}
</script>

<template>
  <img
    ref="image"
    :src="src"
    :style="{
      width: `${width}px`,
      height: `${height}px`,
    }"
    @error="onError"
  >
</template>
