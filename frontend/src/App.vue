<script setup>
import { onMounted } from 'vue'
import NotificationArea from '@/components/common/NotificationArea.vue'

// Previne o comportamento padrão de drag & drop do navegador globalmente
onMounted(() => {
  const preventEvent = evt => evt.preventDefault()
  window.addEventListener('dragover', preventEvent, false)
  window.addEventListener('drop', preventEvent, false)
})
</script>

<template>
  <div id="app" class="min-h-screen bg-white text-black font-sans antialiased selection:bg-primary selection:text-white">
    <!-- Renderizador de rotas do Vue Router -->
    <RouterView />
    <NotificationArea />
  </div>
</template>
