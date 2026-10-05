<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: {
    type: Object,
    default: null,
  },
  label: {
    type: String,
    default: '',
  },
  resultKey: {
    type: String,
    default: '',
  },
  totalKey: {
    type: String,
    default: '',
  },
  total: {
    type: Object,
    default: () => ({}),
  },
  useAmount: {
    type: Boolean,
    default: false,
  },
  useCreditors: {
    type: Boolean,
    default: false,
  },
  color: {
    type: String,
    default: '',
  },
  withoutAbstention: {
    type: Boolean,
    default: false,
  },
  toPrint: {
    type: Boolean,
    default: false,
  },
})

const usePercentage = (value, total) =>
  getPercentage(value, total)?.toFixed(2) + '%'

const abstention = computed(() => props.result?.abstentionChoice)
</script>

<template>
  <div v-if="result">
    <div class="font-bold text--content/50 uppercase mb-3">
      <div class="text--content overflow-hidden text-ellipsis">
        {{ label ? label : result?.name }}:
      </div>
      <div v-if="useCreditors" class="text-3">
        {{ result?.votedCreditors }} de {{ result?.qualifiedCreditors ?? 0 }} credores
        <span class="bg--content/40 px-1 rounded-1 color--base">{{ usePercentage(result?.votedCreditors, result?.qualifiedCreditors) }}</span>
      </div>
      <div v-if="useAmount" class="text-3">
        {{ formatMoney(result?.votedAmount) }} de {{ formatMoney(result?.qualifiedAmount) }}
        <span class="bg--content/40 px-1 rounded-1 color--base">{{ usePercentage(result?.votedAmount, result?.qualifiedAmount) }}</span>
      </div>
      <div v-if="!useAmount || !useCreditors" class="opacity-0">
        -
      </div>
    </div>
    <div class="pr-4 grid gap-y-3">
      <div v-for="choice in result.choices" :key="choice?.id" class="grid grid-cols-[40%_60%] gap-y-1 items-center">
        <div>{{ choice?.label ?? '-' }}</div>
        <Progress
          v-if="useCreditors"
          :percentage="getPercentage(choice?.creditors, result?.votedCreditors)"
          :color="color ? color : undefined"
          :label="toPrint ? undefined : 'credores'"
        />
        <span v-if="useAmount && useCreditors" />
        <Progress
          v-if="useAmount"
          :percentage="getPercentage(choice?.amount, result?.votedAmount)"
          :color="color
            ? color : useCreditors
              ? 'secondary' : 'primary'"
          :label="toPrint ? undefined : 'créditos'"
        />
      </div>
      <div v-if="totalKey && resultKey" class="grid grid-cols-[40%_60%]">
        <div>{{ label }}</div>
        <Progress
          :label="toPrint ? undefined : 'total'"
          :color="color ? color : 'secondary'"
          :percentage="getPercentage(result[resultKey], total[totalKey])"
        />
      </div>
      <div v-if="withoutAbstention && abstention" class="grid grid-cols-[40%_60%] gap-y-1 items-center">
        <div>Abstenção</div>
        <Progress
          v-if="useCreditors"
          :label="toPrint ? undefined : 'credores'"
          color="dark-warning"
          :percentage="getPercentage(result?.qualifiedCreditors - result?.votedCreditors, result?.qualifiedCreditors)"
        />
        <div v-if="useAmount && useCreditors" />
        <Progress
          v-if="useAmount"
          :label="toPrint ? undefined : 'créditos'"
          :color="useAmount && useCreditors ? 'warning' : 'dark-warning'"
          :percentage="getPercentage(result?.qualifiedAmount - result?.votedAmount, result?.qualifiedAmount)"
        />
      </div>
    </div>
  </div>
</template>