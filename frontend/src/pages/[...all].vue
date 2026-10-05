<script setup>
const router = useRouter()
</script>

<template>
  <Page>
    <div class="flex justify-center items-center p-4 max-w-400 min-w-60 mx-auto h-full">
      <div>
        <h1 class="font-bold text-5xl">
          Parece que não tem nada por aqui...
        </h1>
        <Btn
          label="Voltar para a Home"
          icon="i-carbon-home"
          class="lg:mx-auto mt-4"
          @click="router.push('/')"
        />
      </div>
    </div>
  </Page>
</template>