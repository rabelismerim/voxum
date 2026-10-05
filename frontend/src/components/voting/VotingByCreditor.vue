<script setup>
import { ref, computed, watchEffect } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
  },
  creditor: {
    type: Object,
    default: () => ({}),
  },
  choices: {
    type: Array,
    default: () => [],
  },
  corporateMode: {
    type: Boolean,
  },
})

const emit = defineEmits(['update:open', 'update:creditor', 'success', 'close'])

const { dialog } = useQuasar()

function cloneObj(obj) {
  if (!obj) return {}
  return typeof structuredClone === 'function'
    ? structuredClone(obj)
    : JSON.parse(JSON.stringify(obj))
}

const localCreditor = ref(cloneObj(props.creditor))

watchEffect(() => {
  localCreditor.value = cloneObj(props.creditor)
})

const hasReservations = ref(false)
const selectedChoice = ref(null)
const loading = ref(false)

function clear() {
  selectedChoice.value = null
  hasReservations.value = false
  emit('update:creditor', {})
}

const creditorName = computed(() => `${localCreditor.value?.guest?.user?.firstName ?? ''} ${localCreditor.value?.guest?.user?.lastName ?? ''}`)
const legalNumber = computed(() => props.creditor?.guest?.entity?.legalNumber || '')

function votingBy() {
  if (!selectedChoice.value) {
    throwError?.({ id: 'voting_choice', message: 'Você precisa selecionar uma opção para votar!' })
    return
  }

  dialog({
    title: 'Votando por Credor',
    message: `Você confirma que o Credor "${creditorName.value}" requisitou esta ação?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    loading.value = true
    try {
      const method = props.corporateMode ? 'voteForCreditor' : 'creditorVote'
      const result = await votingService[method](
        props.creditor?.id,
        selectedChoice.value,
        hasReservations.value,
        props.creditor?.result
      )
      if (!result?.id) return

      notify?.({ message: 'Votação registrada com sucesso!' })
      emit('success')
      emit('update:open', false)
      clear()
    }
    catch (error) {
      console.error('ERROR ON REGISTRING VOTING BY:', error)
    }
    finally {
      loading.value = false
    }
  })
}

function onModalClose(value) {
  clear()
  emit('update:open', value)
  if (!value) emit('close')
}
</script>

<template>
  <Modal
    :title="`Votando por ${creditorName}`"
    :subtitle="`${legalNumber?.length > 11 ? 'CNPJ' : 'CPF'}: ${formatLegalNumber(legalNumber)}`"
    :model-value="open"
    modal-class="max-w-180"
    @update:model-value="onModalClose"
  >
    <QForm @submit="votingBy">
      <div class="p-4 grid grid-cols-2 gap-3">
        <div
          v-for="(choice, index) in choices"
          :key="index"
          class="border-1 border--content/12 rounded-1 p-2 text-4 hover:bg--secondary/20 cursor-pointer"
          :class="{
            'bg--secondary text-white hover:bg--secondary!': selectedChoice === choice.choices[creditor?.classe?.description],
          }"
          @click="selectedChoice = choice.choices[creditor?.classe?.description]"
        >
          {{ choice.value }}
        </div>
      </div>
      <div class="p-3 border-t-1 border--content/12 flex justify-between">
        <QToggle v-model="hasReservations" label="Com ressalva" />
        <Btn
          label="Votar"
          :disabled="!selectedChoice"
          :tooltip="!selectedChoice ? 'Selecione uma opção para votar!' : null"
          loading-label="Registrando Voto..."
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