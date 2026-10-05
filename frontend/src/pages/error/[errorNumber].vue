<script setup>
const attrs = useAttrs()
const params = useUrlSearchParams('history')

const open = $ref(false)

const defaultError = 'Parece que aconteceu\num erro no sistema...\nvolte mais tarde.'
const messages = {
  500: defaultError,
  401: 'Parece que você\nprecisa estar logado\npara acessar!',
  403: 'Parece que você\nnão tem permissão\nde acesso!',
  404: 'Parece que essa\ninformação não foi\nencontrada...',
}
</script>

<template>
  <Page>
    <div class="flex justify-center items-center p-4 max-w-400 min-w-60 mx-auto h-full">
      <div>
        <h1 class="font-bold text-5xl mb-3">
          Erro {{ attrs.errorNumber }}
        </h1>
        <div class="text-6 line-height-7">
          <div class="whitespace-pre">
            {{ messages[attrs.errorNumber] ?? defaultError }}
          </div>
          <Btn
            v-if="params.detail"
            :label="`${open ? 'Menos' : 'Mais'} detalhes...`"
            color="error"
            transparent
            class="mt-3 -ml-4"
            @click="open = !open"
          />
        </div>
      </div>
    </div>
    <template #bottom>
      <Expandable
        v-if="params.detail"
        v-model:open="open"
        content-class="p-0"
      >
        <template #header />
        <div class="whitespace-pre-wrap bg--error/12 pt-4 border-t-1 border--content/12 border--error text--error">
          <div class="relative px-3 text-6 font-bold mb-2">
            Detalhe do Erro:
            <BtnIcon
              icon="i-carbon-close"
              color="error"
              transparent
              class="absolute! right-4 top-0 rounded-full"
              @click="open = false"
            />
          </div>
          <div class="max-h-60vh overflow-y-auto px-4 pb-4">
            {{ params.detail }}
          </div>
        </div>
      </Expandable>
    </template>
  </Page>
</template>

<route lang="yaml">
meta:
  layout: splash
</route>