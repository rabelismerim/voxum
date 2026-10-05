<script setup>
const props = defineProps({
  socket: {
    type: Object,
    default: () => ({ status: '' }),
  },
})
const emit = defineEmits(['click'])

const socket = $computed(() => props.socket)
const isLoading = $computed(() => ['UNSET', 'CONNECTING'].includes(socket.status))
const isConnected = $computed(() => socket.status === 'CONNECTED')
const isClosed = $computed(() => socket.status === 'CLOSED')
</script>

<template>
  <StatusTag
    :class="{
      'cursor-pointer': isClosed,
      'cursor-wait': isLoading,
    }"
    :label="isLoading ? 'conectando...' : isConnected ? 'online' : 'problemas na conexão'"
    :color="isLoading ? '#007db3' : isConnected ? '#87bb25' : '#d9291c'"
    :tooltip="isClosed ? 'Clique para reconectar...' : ''"
    @click="emit('click', $event)"
  />
</template>
