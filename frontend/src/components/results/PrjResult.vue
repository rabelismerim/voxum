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

const dataColumnCount = computed(() => Math.min(props.results.length + 1, 4))

const data = computed(() => mapResults(props.results, props.withAbstention))

const articlesResults = computed(() => ({
  ...data.value.choices.reduce((acc, { name, choices, votedCreditors, votedAmount }) => {
    const className = `classe${name.split('-').at(0).trim().toUpperCase().split(' ').at(1)}`
    const yesChoice = choices.find(({ label }) => label.toLowerCase().includes('sim'))
    acc[className] = {
      creditors: yesChoice?.creditors || 0,
      votedCreditors,
      amount: yesChoice?.amount || 0,
      votedAmount,
    }
    return acc
  }, {}),
  total: {
    creditors: data.value.total.votedCreditors,
    amount: data.value.total.votedAmount,
  },
}))

const article45 = computed(() => {
  const { classeI: cI, classeII: cII, classeIII: cIII, classeIV: cIV } = articlesResults.value
  const hasSome = [cI, cII, cIII, cIV].some(e => !!e)
  const classeI = hasSome && !cI?.votedCreditors ? true : cI?.creditors > (1 / 2) * cI?.votedCreditors
  const classeII = hasSome && !cII?.votedCreditors ? true : cII?.creditors > (1 / 2) * cII?.votedCreditors && cII?.amount > (1 / 2) * cII?.votedAmount
  const classeIII = hasSome && !cIII?.votedCreditors ? true : cIII?.creditors > (1 / 2) * cIII?.votedCreditors && cIII?.amount > (1 / 2) * cIII?.votedAmount
  const classeIV = hasSome && !cIV?.votedCreditors ? true : cIV?.creditors > (1 / 2) * cIV?.votedCreditors
  const accepted = hasSome && classeI && classeII && classeIII && classeIV
  return { classeII, classeIII, classeI, classeIV, accepted }
})

const article58 = computed(() => {
  const { classeI, classeII, classeIII, classeIV, total } = articlesResults.value
  const classes = [classeI, classeII, classeIII, classeIV]
  const { classeI: acceptedClasseI, classeII: accepetedClasseII, classeIII: accepetedClasseIII, classeIV: accepetedClasseIV } = article45.value
  const acceptedClasses = [acceptedClasseI, accepetedClasseII, accepetedClasseIII, accepetedClasseIV]
  const inciseI = classes.reduce((acc, cur) => acc + (cur?.amount ?? 0), 0) > (1 / 2) * total?.amount
  const inciseII = acceptedClasses.filter(classe => !!classe).length >= (classes.length - 1)
  const notValidatedIndex = acceptedClasses.findIndex(classe => !classe)
  const notValidated = classes[notValidatedIndex]
  const inciseIII = notValidatedIndex < 0 && inciseII
    ? true
    : !inciseII
      ? false
      : [0, 3].includes(notValidatedIndex)
        ? notValidated?.creditors > (1 / 3) * notValidated?.votedCreditors
        : notValidated?.creditors > (1 / 3) * notValidated?.votedCreditors && notValidated?.amount > (1 / 3) * notValidated?.votedAmount
  const accepted = inciseI && inciseII && inciseIII
  return { inciseI, inciseII, inciseIII, accepted }
})

const onClasses = result => !['classe i', 'classe iv']
  .some(classe => result?.name?.split('-')?.at(0)?.trim()?.toLowerCase() === classe)
</script>

<template>
  <div>
    <div
      class="grid gap-4"
      :style="{
        gridTemplateColumns: width < 450
          ? 'repeat(1,minmax(0,1fr))'
          : width < 800
            ? 'repeat(2,minmax(0,1fr))'
            : `repeat(${dataColumnCount},minmax(0,1fr))`,
      }"
    >
      <ResultCell
        v-for="result in data.choices"
        :key="result.classe"
        :result="result"
        use-creditors
        :use-amount="onClasses(result)"
        :to-print="toPrint"
        :without-abstention="!withAbstention"
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
        Créditos
      </span>
    </div>
    <div v-if="showDetail" class="mt-2 text-3 grid grid-cols-1 lg:grid-cols-2 gap-y-2 gap-x-4">
      <div class="grid grid-cols-[1.8fr_4.1fr_4.1fr] gap-1 items-center mr-4">
        <div class="font-bold text-4">Artigo 45</div>
        <div class="col-span-2" />
        <div class="grid grid-cols-[1.8fr_8.2fr] col-span-3">
          <div>Parágrafo I</div>
          <div class="px-1 text-balance">maior que 50% dos credores presentes e maior que 50% dos créditos dos presentes das Classes II e III</div>
          <div>Parágrafo II</div>
          <div class="px-1 text-balance">maior que 50% dos credores presentes das classes I e IV</div>
        </div>
        <div>Parágrafo I</div>
        <div class="text-center p-1 rounded-1" :class="[article45.classeII ? 'bg--success/50' : 'bg--error/30']">Classe II - {{ article45.classeII ? 'sim' : 'não' }} atendido</div>
        <div class="text-center p-1 rounded-1" :class="[article45.classeIII ? 'bg--success/50' : 'bg--error/30']">Classe III - {{ article45.classeIII ? 'sim' : 'não' }} atendido</div>
        <div>Parágrafo II</div>
        <div class="text-center p-1 rounded-1" :class="[article45.classeI ? 'bg--success/50' : 'bg--error/30']">Classe I - {{ article45.classeI ? 'sim' : 'não' }} atendido</div>
        <div class="text-center p-1 rounded-1" :class="[article45.classeIV ? 'bg--success/50' : 'bg--error/30']">Classe IV - {{ article45.classeIV ? 'sim' : 'não' }} atendido</div>
        <div>Atendido</div>
        <div class="col-span-2 text-center p-1 rounded-1" :class="[article45.accepted ? 'bg--success/50' : 'bg--error/30']">{{ article45.accepted ? 'Sim' : 'Não' }} atendido</div>
      </div>
      <div class="grid grid-cols-[2fr_6fr_2fr] gap-1 items-center mr-4">
        <div class="font-bold text-4">Artigo 58</div>
        <div class="col-span-2" />
        <div>Inciso I</div>
        <div class="px-1">maior que 50% do total dos créditos de todos os presentes</div>
        <div class="text-center p-1 rounded-1 min-w-22" :class="[article58.inciseI ? 'bg--success/50' : 'bg--error/30']">{{ article58.inciseI ? 'Sim' : 'Não' }} atendido</div>
        <div>Inciso II</div>
        <div class="px-1">total de classes presentes menos 1, no Artigo 45 que foram atendidos</div>
        <div class="text-center p-1 rounded-1 min-w-22" :class="[article58.inciseII ? 'bg--success/50' : 'bg--error/30']">{{ article58.inciseII ? 'Sim' : 'Não' }} atendido</div>
        <div>Inciso III</div>
        <div class="px-1">o único que não passou precisa de 1/3 na forma do Artigo 45</div>
        <div class="text-center p-1 rounded-1 min-w-22" :class="[article58.inciseIII ? 'bg--success/50' : 'bg--error/30']">{{ article58.inciseIII ? 'Sim' : 'Não' }} atendido</div>
        <div>Cram Down</div>
        <div class="col-span-2 text-center p-1 rounded-1" :class="[article58.accepted ? 'bg--success/50' : 'bg--error/30']">{{ article58.accepted ? 'Sim' : 'Não' }} atendido</div>
      </div>
    </div>
  </div>
</template>