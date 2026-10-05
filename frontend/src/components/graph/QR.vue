<script setup>
import { ref, onMounted } from 'vue'
import QrCreator from 'qr-creator'

const props = defineProps({
  content: {
    type: String,
    default: 'Hello world!',
  },
  smallSize: {
    type: Number,
    default: 68,
  },
  bigSize: {
    type: Number,
    default: 400,
  },
})

const { isMobile } = useAmbient()

const showModal = ref(false)
const qrSmall = ref(null)
const qrBig = ref(null)

const radius = 0
const background = null
const fill = '#444'

onMounted(() => {
  if (qrSmall.value) {
    QrCreator.render({
      text: props.content,
      size: props.smallSize,
      ecLevel: 'L',
      radius,
      fill,
      background,
    }, qrSmall.value)
  }
  if (qrBig.value) {
    QrCreator.render({
      text: props.content,
      size: props.bigSize,
      ecLevel: 'H',
      radius,
      fill,
      background,
    }, qrBig.value)
  }
})
</script>

<template>
  <div>
    <div ref="qrSmall" class="bg-white p-2 cursor-pointer rounded-1" @click="showModal = true">
      <QTooltip v-if="!isMobile()">
        Clique para expandir o QR Code
      </QTooltip>
    </div>
    <Modal
      v-model="showModal"
      hide-title
      not-stack
      modal-class="max-w-[calc(100vh-32px)] w-[min-content]! overflow-hidden color-black"
    >
      <div ref="qrBig" class="qr-big p-6vmin w-[min-content] aspect-square bg-white" />
    </Modal>
  </div>
</template>

<style>
.qr-big > canvas {
  width: calc(78vmin - 3rem);
}
</style>