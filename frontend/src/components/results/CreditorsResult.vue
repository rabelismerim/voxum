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
})

const data = computed(() => mapResults(props.results, props.withAbstention))
</script>

<template>
  <div
    class="grid gap-4"
    :style="{
      gridTemplateColumns: width < 450
        ? 'repeat(1,minmax(0,1fr))'
        : width < 960
          ? 'repeat(2,minmax(0,1fr))'
          : 'repeat(auto-fit,minmax(0,1fr))',
    }"
  >
    <ResultCell
      v-for="result in data.choices"
      :key="result.classe"
      :label="result.classe"
      :result="result"
      use-creditors
      :total-key="withAbstention ? 'qualifiedCreditors' : 'votedCreditors'"
      result-key="votedCreditors"
      :total="data.total"
      :to-print="toPrint"
      :without-abstention="!withAbstention"
    />
    <ResultCell
      :result="data.total"
      label="Total"
      color="secondary"
      use-creditors
      :total-key="withAbstention ? 'qualifiedCreditors' : 'votedCreditors'"
      result-key="votedCreditors"
      :total="data.total"
      :to-print="toPrint"
      :without-abstention="!withAbstention"
    />
  </div>
  <div v-if="toPrint" class="mt-4 pr-4 text-right">
    <span class="font-bold mr-2">Legenda:</span>
    <span class="mr-2 items-center">
      <div class="h-4 w-4 bg--primary rounded-1 inline-block translate-y-.5 mr-1" />
      Credores por Classe
    </span>
    <span class="items-center">
      <div class="h-4 w-4 inline-block bg--secondary rounded-1 translate-y-.5 mr-1" />
      Totais
    </span>
  </div>
</template>