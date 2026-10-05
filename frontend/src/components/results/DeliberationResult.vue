<script setup>
import { computed } from 'vue'

const props = defineProps({
  results: {
    type: Array,
    default: () => [],
  },
  width: {
    type: Number,
    default: 0,
  },
  withAbstention: {
    type: Boolean,
    default: false,
  },
  toPrint: {
    type: Boolean,
    default: false,
  },
  showDetail: {
    type: Boolean,
    default: false,
  },
})

const data = computed(() => mapResults(props.results, props.withAbstention))
</script>

<template>
  <div class="grid grid-cols-[1fr_9fr] mr-4 gap-3">
    <div class="font-bold uppercase col-span-2">Total por Crédito:</div>
    <template
      v-for="result in data.total.choices"
      :key="result.label"
    >
      <div>{{ result.label }}</div>
      <Progress
        :label="toPrint ? undefined : result.label"
        color="primary"
        :percentage="getPercentage(result.amount, data.total?.votedAmount)"
      />
    </template>
    <div>Total</div>
    <Progress
      :label="toPrint ? undefined : 'Total'"
      color="secondary"
      :percentage="getPercentage(data.total.votedAmount, data.total.qualifiedAmount)"
    />
    <div v-if="!withAbstention">Abstenção</div>
    <Progress
      v-if="!withAbstention"
      :label="toPrint ? undefined : 'Abstenção'"
      color="dark-warning"
      :percentage="getPercentage(data.total.qualifiedAmount - data.total.votedAmount, data.total.qualifiedAmount)"
    />
  </div>
  <div v-if="toPrint" class="mt-4 pr-4 text-right">
    <span class="font-bold mr-2">Legenda:</span>
    <span class="mr-2 items-center">
      <div class="h-4 w-4 bg--primary rounded-1 inline-block translate-y-.5 mr-1" />
      Credores
    </span>
    <span class="items-center">
      <div class="h-4 w-4 inline-block bg--secondary rounded-1 translate-y-.5 mr-1" />
      Créditos Votados
    </span>
  </div>
  <div v-if="showDetail" class="mt-2 text-3 gap-y-2 gap-x-4">
    <div class="font-bold text-4">Artigo 42</div>
    <div class="text-balance">
      Considerar‑se‑á aprovada a proposta que obtiver votos favoráveis
      de credores que representem mais da metade do valor total dos
      créditos presentes à assembleia geral, exceto nas deliberações sobre
      o plano de recuperação judicial nos termos da alínea a do inciso I
      do caput do art. 35 desta Lei, a composição do Comitê de Credores
      ou forma alternativa de realização do ativo nos termos do art. 145
      desta Lei.
    </div>
  </div>
</template>