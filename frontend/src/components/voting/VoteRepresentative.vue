<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
  },
  voting: {
    type: Object,
    default: () => ({}),
  },
  meeting: {
    type: Object,
    default: () => ({}),
  },
  choiceOptions: {
    type: Array,
    default: () => [],
  },
  creditorVotings: {
    type: Object,
    default: () => ({}),
  },
  creditorCaveats: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:open', 'success', 'cancel'])

const loading = ref(false)

const creditorsChoices = computed(() => Object.values(props.creditorVotings))

const choicesWithCount = computed(() =>
  props.choiceOptions.map(({ value, choices }) => ({
    value,
    count: creditorsChoices.value.filter(choice => Object.values(choices).includes(choice)).length,
  }))
)

async function submitVote() {
  loading.value = true
  if (!props.meeting?.id) return

  try {
    const creditorsVoting = Object.entries(props.creditorVotings).map(([creditorId, voteId]) => ({
      creditorId,
      voteId,
      hasReservations: !!props.creditorCaveats[creditorId],
    }))

    const { taskId } = (await votingService.representativeVote(props.meeting?.id, creditorsVoting)) ?? {}
    if (taskId) {
      notify?.({ message: 'Voto computado!' })
      emit('update:open', false)
      emit('success', taskId)
    }
  }
  catch (error) {
    console.error('ERROR IN SENDING THE VOTE:', error)
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <Modal
    hide-close
    :loading="loading"
    :model-value="open"
    :title="`Votação: ${voting?.description}`"
    subtitle="Verifique o total de votos para cada opção antes de enviar."
    modal-class="md:max-w-150"
  >
    <div>
      <div class="px-4 pb-3">
        <div class="text-4 mb-3 text-bold">
          As opções se configuraram da seguinte maneira:
        </div>
        <div
          v-for="({ value, count }, index) in choicesWithCount"
          :key="index"
          class="p-4 mb-1 border--secondary border-l-5 flex justify-between bg-indigo-1"
        >
          <div class="text-bold text-4">
            {{ value }}
          </div>
          <div class="px-3 py-1 bg-black/10 rounded-full">
            <span class="font-bold">{{ count }}</span> credor{{ count > 1 ? 'es' : '' }}
          </div>
        </div>
      </div>

      <div class="p-3 flex gap-4 justify-end border-t-1 border--content/12">
        <Btn
          label="Cancelar"
          outlined
          color="primary"
          @click="emit('update:open', false); emit('cancel')"
        />
        <Btn
          label="Enviar Voto"
          color="primary"
          :loading="loading"
          loading-label="Registrando votos..."
          @click="submitVote"
        />
      </div>
    </div>
  </Modal>
</template>