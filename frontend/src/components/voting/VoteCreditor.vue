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
  choice: {
    type: Object,
    default: () => ({}),
  },
  taskId: {
    type: String,
  },
})

const emit = defineEmits(['update:open', 'newTask', 'success'])

const loading = ref(false)
const isComputed = ref(false)
const hasReservations = ref(false)

const choices = computed(() =>
  Object.entries(props.choice ?? {}).map(([classe, choiceItem]) => ({ classe, ...choiceItem }))
)

async function submitVote() {
  isComputed.value = true
  loading.value = true
  try {
    for (const choiceItem of choices.value) {
      const { taskId } = (await votingService.creditorVote(choiceItem?.creditorId, choiceItem?.id, hasReservations.value)) ?? {}
      if (taskId) emit('newTask', taskId)
    }
  }
  catch (error) {
    console.error('ERROR IN SENDING THE VOTE:', error)
  }
  finally {
    loading.value = false
    emit('success')
    emit('update:open', false)
  }
}
</script>

<template>
  <Modal
    :loading="loading"
    hide-close
    :model-value="open"
    :title="`Votação: ${voting?.description ?? ''}`"
    subtitle="Verifique o seu Voto antes de enviar."
    modal-class="md:max-w-150"
  >
    <div>
      <div class="px-4 pb-3">
        <div class="text-4 mb-3 text-bold">
          A opção selecionada foi:
        </div>
        <div class="p-4 mb-1 border--secondary border-l-5 flex flex-col gap-3 bg--content/5">
          <div
            v-for="choiceItem in choices"
            :key="choiceItem.votingId"
            class="text-bold text-4 flex flex-nowrap gap-2 items-center"
          >
            <div class="px-2 border-1 border--content/12 rounded-full bg--content/10">
              {{ choiceItem.classe }}
            </div>
            {{ choiceItem.value }}
          </div>
        </div>
      </div>

      <div class="p-3 flex gap-4 justify-between border-t-1 border--content/12">
        <Toggle
          v-model="hasReservations"
          label="Com ressalva"
          :disabled="isComputed"
        />
        <div class="flex gap-4">
          <Btn
            label="Cancelar"
            outlined
            color="primary"
            :disabled="loading"
            @click="emit('update:open', false)"
          />
          <Btn
            label="Enviar Voto"
            color="primary"
            :loading="loading"
            loading-label="Enviando Voto..."
            :disabled="isComputed"
            @click="submitVote"
          />
        </div>
      </div>
    </div>
  </Modal>
</template>