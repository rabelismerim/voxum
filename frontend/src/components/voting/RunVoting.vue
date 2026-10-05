<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  voting: {
    type: Object,
    default: () => ({}),
  },
  type: {
    type: String,
    default: 'start',
  },
})

const emit = defineEmits(['update:open', 'success', 'close'])

const loading = ref(false)

const nullTime = {
  hours: 0,
  minutes: 10,
  seconds: 0,
}

function cloneObj(obj) {
  if (!obj) return {}
  return typeof structuredClone === 'function'
    ? structuredClone(obj)
    : JSON.parse(JSON.stringify(obj))
}

const time = ref(cloneObj(nullTime))

function clearTime() {
  time.value = cloneObj(nullTime)
}

const formatedTime = computed(() =>
  Object.values(time.value)
    .map(value => value.toString().padStart(2, '0'))
    .join(':')
)

async function runVoting() {
  loading.value = true
  try {
    const method = props.type === 'start' ? 'start' : 'extend'
    await votingService[method](props.voting.id, formatedTime.value)
    notify?.({ message: `Votação ${props.type === 'start' ? 'iniciada' : 'prorrogada'} com sucesso!` })
    clearTime()
    emit('update:open', false)
  }
  catch (error) {
    console.error('ERROR ON STARTING OR EXTENDING MEETING:', error)
  }
  finally {
    loading.value = false
  }
}

function clampInput(event, prop, minValue, maxValue) {
  const { min, max, abs } = Math
  const value = min(max(abs(+event.target.value), minValue), maxValue)
  event.target.value = value
  time.value[prop] = value
}

function onModalClose() {
  clearTime()
  emit('update:open', false)
}
</script>

<template>
  <Modal
    :title="`${type === 'start' ? 'Inici' : 'Prorrog'}ar Votação: ${voting.description ?? ''}`"
    :subtitle="`Tempo de ${type === 'start' ? 'dur' : 'prorrog'}ação da votação!`"
    :model-value="open"
    modal-class="max-w-140"
    @update:model-value="onModalClose"
  >
    <QForm @submit.prevent="runVoting">
      <div class="px-4 py-4 text-10 flex justify-center gap-4 flex-nowrap font-bold">
        <input
          :value="time.hours"
          type="number"
          max="23"
          min="0"
          class="w-20% bg-slate/20 border-1 border--content/12 p-2 text-center rounded-1"
          @input="clampInput($event, 'hours', 0, 23)"
        >:
        <input
          :value="time.minutes"
          type="number"
          max="59"
          min="0"
          class="w-20% bg-slate/20 border-1 border--content/12 p-2 text-center rounded-1"
          @input="clampInput($event, 'minutes', 0, 59)"
        >:
        <input
          :value="time.seconds"
          type="number"
          max="59"
          min="0"
          class="w-20% bg-slate/20 border-1 border--content/12 p-2 text-center rounded-1"
          @input="clampInput($event, 'seconds', 0, 59)"
        >
      </div>
      <div class="p-3 border-t-1 border--content/12 flex justify-end">
        <Btn
          :label="type === 'start' ? 'Iniciar' : 'Prorrogar'"
          :loading-label="`${type === 'start' ? 'Inici' : 'Prorrog'}ando Votação...`"
          :loading="loading"
        />
      </div>
    </QForm>
  </Modal>
</template>

<route lang="yaml">
meta:
  authenticated: true
  permissions: [can_manage_project]
</route>