<script setup>
import { computed } from 'vue'

const props = defineProps({
  reportType: {
    type: String,
    default: 'count',
  },
  meeting: {
    type: Object,
    required: true,
  },
})

const meeting = computed(() => props.meeting)
const presenceStatus = computed(() => meeting.value?.creditorsPresenceStatus ?? [])

const presenceResultCount = computed(() => {
  const { present, total } = presenceStatus.value.reduce(
    (acc, { countAccredited, countCreditors }) => {
      acc.total += countCreditors
      acc.present += countAccredited
      return acc
    },
    { present: 0, total: 0 }
  )
  return { present, total, percentage: total ? (present / total) * 100 : 0 }
})

const presenceResultAmount = computed(() => {
  const { present, total } = (meeting.value?.creditorsCredit ?? []).reduce(
    (acc, { totalCreditAccredited, totalCredit }) => {
      acc.total += totalCredit
      acc.present += totalCreditAccredited
      return acc
    },
    { present: 0, total: 0 }
  )
  return { present, total, percentage: total ? (present / total) * 100 : 0 }
})
</script>

<template>
  <div class="grid gap-4">
    <div class="grid grid-cols-[15rem_1fr] gap-2 items-stretch">
      <template
        v-for="result in ((reportType === 'amount' ? meeting.creditorsCredit : meeting.creditorsPresenceStatus) ?? [])"
        :key="result.classe"
      >
        <div class="font-bold text-gray uppercase flex gap-2">
          {{ result.name }}:
          <div v-if="reportType === 'count'">
            <div>{{ result.countAccredited }} de {{ result.countCreditors }}</div>
          </div>
          <div v-if="reportType === 'amount'">
            <div>{{ formatMoney(result?.totalCreditAccredited) }}</div>
            <div>de {{ formatMoney(result?.totalCredit) }}</div>
          </div>
        </div>
        <Progress
          :percentage="result.percentageAccredited"
          grow
        />
      </template>
    </div>
    <div>
      <div class="font-bold text-gray uppercase mb-2 flex gap-2">
        Total:
        <div v-if="reportType === 'count'">
          <div>{{ presenceResultCount.present }} de {{ presenceResultCount.total }} credores</div>
        </div>
        <div v-if="reportType === 'amount'">
          <div>{{ formatMoney(presenceResultAmount.present) }} de {{ formatMoney(presenceResultAmount.total) }}</div>
        </div>
      </div>
      <Progress
        label="Total"
        :percentage="notNaN((reportType === 'count' ? presenceResultCount : presenceResultAmount).percentage)"
        color="secondary"
      />
    </div>
  </div>
</template>