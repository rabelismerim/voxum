<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  voting: {
    type: Object,
    required: true,
  },
})

const reportType = ref('count') // 'count' | 'amount'

const voting = computed(() => props.voting)
const results = computed(() => voting.value?.results ?? [])

const resultTotal = computed(() => {
  const { parcial, total } = results.value.reduce(
    (acc, { countVoters, countQualifiedCreditors, totalVotersCreditValue, totalCreditValue }) => {
      acc.total += reportType.value === 'count' ? countQualifiedCreditors : totalCreditValue
      acc.parcial += reportType.value === 'count' ? countVoters : totalVotersCreditValue
      return acc
    },
    { parcial: 0, total: 0 }
  )
  return { parcial, total, percentage: total ? (parcial / total) * 100 : 0 }
})
</script>

<template>
  <div class="flex mb-4">
    <BtnToggle
      v-model="reportType"
      :options="{
        count: 'Credores',
        amount: 'Créditos',
      }"
    />
  </div>
  <div class="grid gap-4">
    <div class="grid grid-cols-[15rem_1fr] gap-2 items-stretch">
      <template
        v-for="result in results"
        :key="result.classe"
      >
        <div class="font-bold text-gray uppercase flex gap-2">
          {{ result.name }}:
          <div v-if="reportType === 'count'">
            <div>{{ result.countVoters }} de {{ result.countQualifiedCreditors }}</div>
          </div>
          <div v-if="reportType === 'amount'">
            <div>{{ formatMoney(result?.totalVotersCreditValue) }}</div>
            <div>de {{ formatMoney(result?.totalCreditValue) }}</div>
          </div>
        </div>
        <Progress
          :percentage="reportType === 'count' ? result.percentageVoters : (result?.totalVotersCreditValue / (result?.totalCreditValue || 1)) * 100"
          grow
        />
      </template>
    </div>
    <div>
      <div class="font-bold text-gray uppercase mb-2 flex gap-2">
        Total:
        <div v-if="reportType === 'count'">
          <div>{{ resultTotal?.parcial }} de {{ resultTotal?.total }} credores</div>
        </div>
        <div v-if="reportType === 'amount'">
          <div>{{ formatMoney(resultTotal?.parcial) }} de {{ formatMoney(resultTotal?.total) }}</div>
        </div>
      </div>
      <Progress
        label="Total"
        :percentage="notNaN(resultTotal.percentage)"
        color="secondary"
      />
    </div>
  </div>
</template>