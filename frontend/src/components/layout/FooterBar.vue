<script setup>
import links from '@/assets/footer-links.json'

const props = defineProps({
  showLinks: {
    type: Boolean,
    default: false,
  },
})

// Garantia de fallback para variável global APP_VERSION
const appVersion = typeof APP_VERSION !== 'undefined' ? APP_VERSION : '0.0.0'
</script>

<template>
  <footer class="z-100">
    <div
      v-if="showLinks"
      class="flex justify-center p-2 bg--base border-t-1 border--content/12"
    >
      <a
        v-for="({ title, url }, index) in links"
        :key="title"
        :href="url"
        class="px-2"
        :class="{ 'border-l-1 border--content/12': index > 0 }"
        target="_blank"
        rel="noopener noreferrer"
      >
        {{ title }}
      </a>
    </div>
    <div class="text-2.5 md:text-3 flex flex-nowrap items-center justify-between bg-black h-9 px-4 md:px-10 text-white overflow-hidden">
      <div class="inline sm:block">
        © 2024
      </div>
      <span class="ml-4 whitespace-pre">Versão: {{ appVersion }}</span>
    </div>
  </footer>
</template>