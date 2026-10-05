<script setup>
const router = useRouter()
</script>

<template>
  <button
    class="h-8 uppercase group flex gap-1 items-center color--primary font-semibold hover:text--secondary z-1 tween-500"
    @click="router.go(-1)"
  >
    <div class="i-carbon-chevron-left group-hover:-translate-x-1 tween" />
    Voltar
  </button>
</template>
