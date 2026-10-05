<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  meetingId: {
    type: String,
    required: true,
  },
  socket: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:open', 'update:loading', 'click'])

const { dialog } = useQuasar()

const meeting = computed(() => props.socket?.channels?.meetingDetail ?? {})
const voting = computed(() => props.socket?.channels?.votingProgress ?? {})
const hasAccredited = computed(() => meeting.value.situation === 3 || (!meeting.value?.ableToRegisterPresence && meeting.value?.startRegisterPresence))

const {
  pagination: activePagination,
  updatePagination: updateActivePagination,
  items: activeVotings,
  get: loadActiveVotings,
  previousPage: previousActivePage,
  nextPage: nextActivePage,
  onLoad: onLoadActiveVotings,
  onFirstPage: onFirstActivePage,
  onLastPage: onLastActivePage,
  resetPage: resetActivePage,
} = votingService.getVotings(props.meetingId, props.socket, ['I', 'A', 'R'])

updateActivePagination({ filterColumn: 'description' })
onLoadActiveVotings({
  start: () => emit('update:loading', true),
  end: () => emit('update:loading', false),
})

const {
  pagination: endedPagination,
  items: endedVotings,
  get: loadEndedVotings,
  previousPage: goPreviousEndedPage,
  nextPage: goNextEndedPage,
  onLoad: onLoadEndedVotings,
  onFirstPage: onFirstEndedPage,
  onLastPage: onLastEndedPage,
} = votingService.getVotings(props.meetingId, props.socket, ['E'])

onLoadEndedVotings({
  start: () => emit('update:loading', true),
  end: () => emit('update:loading', false),
})

const showNewVoting = ref(false)
const selectedVoting = ref({})
const runVotingType = ref('extend')
const showRunVoting = ref(false)

function runVoting(type, votingItem) {
  if (type !== 'finish') {
    selectedVoting.value = votingItem
    runVotingType.value = type
    showRunVoting.value = true
    return
  }
  endVoting()
}

async function endVoting() {
  dialog({
    title: 'Encerrando Votação',
    message: 'Você confirma o fim dessa Votação?',
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    emit('update:loading', true)
    try {
      await votingService.finish(voting.value.id)
      notify?.({ message: 'Votação encerrada com sucesso!' })
    }
    catch (error) {
      console.error('ERROR ON ENDING MEETING ON VOTING LIST:', error)
    }
    finally {
      emit('update:loading', false)
    }
  })
}

defineExpose({
  endVoting,
  runVoting,
})

onMounted(() => {
  loadActiveVotings()
  loadEndedVotings()
})
</script>

<template>
  <Drawer
    :open="open"
    title="Votações"
    position="left"
    class="border-r-1 border--content/12"
    @click="emit('click')"
  >
    <div class="w-80 flex flex-col flex-nowrap h-full overflow-hidden">
      <div class="flex gap-2 pb-2 flex-nowrap p-2">
        <BtnIcon
          icon="i-carbon-renew"
          outlined
          color="primary"
          tooltip="Recarregar Lista"
          @click="loadActiveVotings"
        />
        <div class="flex flex-nowrap">
          <BtnIcon
            icon="i-carbon-chevron-left"
            outlined
            color="primary"
            tooltip="Página Anterior"
            :disabled="onFirstActivePage"
            class="rounded-r-0"
            @click="previousActivePage"
          />
          <BtnIcon
            icon="i-carbon-chevron-right"
            outlined
            color="primary"
            tooltip="Próxima Página"
            :disabled="onLastActivePage"
            class="rounded-l-0 border-l-0"
            @click="nextActivePage"
          />
        </div>
        <SearchFilter
          v-model:search="activePagination.filterBy"
          hide-label
          class="flex-1"
          @update:search="resetActivePage"
        />
        <BtnIcon
          icon="i-carbon-add"
          color="primary"
          filled
          tooltip="Nova Votação"
          @click="showNewVoting = true"
        />
      </div>

      <div class="flex-1 overflow-y-auto px-2">
        <div v-if="activeVotings?.length" v-auto-animate>
          <button
            v-for="votingData in activeVotings"
            :key="votingData.id"
            class="p-2 hover:bg--secondary/20 rounded cursor-pointer mb-2 flex gap-2 items-center text-left w-full"
            :class="{
              'hover:bg--error/20!': votingData.id === voting.id,
            }"
            :disabled="!hasAccredited"
            @click="runVoting(votingData.id === voting.id ? 'finish' : 'start', votingData)"
          >
            <div
              class="flex-1"
              :class="{
                'font-bold': votingData.id === voting.id,
              }"
            >
              <div>{{ votingData.description }}</div>
              <div class="flex gap-2 items-center">
                <div class="px-2 py-.5 bg-gray/20 text-3 rounded-full">
                  {{ votingData.typeDisplay }}
                </div>
                <div
                  class="px-2 py-.5 rounded-full text-white text-3"
                  :style="{
                    background: votingData.statusColor,
                  }"
                >
                  {{ votingData.statusDisplay }}
                </div>
              </div>
            </div>
            <div v-if="votingData.id !== voting.id" class="i-carbon-play-filled-alt text--secondary" />
            <div v-else class="i-carbon-stop-filled-alt text--error" />
            <QTooltip>
              {{ !hasAccredited ? 'Você precisa iniciar o credenciamento antes!' : votingData.id === voting.id ? 'Encerrar Votação' : 'Iniciar Votação' }}
            </QTooltip>
          </button>
        </div>
        <div v-else class="px-2 py-4 color-gray-5">
          Nenhuma Votação Ativa encontrada...
        </div>

        <Expandable
          title="Votações Finalizadas"
          icon-right="i-carbon-chevron-right"
          hide-icon
          title-class="pl-2 py-1 rounded"
          content-class="p-0"
        >
          <div class="flex gap-2 py-2 flex-nowrap pr-2 items-center justify-between">
            <div class="flex flex-nowrap gap-2">
              <BtnIcon
                icon="i-carbon-renew"
                outlined
                color="primary"
                tooltip="Recarregar Lista"
                @click="loadEndedVotings"
              />
              <div class="flex flex-nowrap">
                <BtnIcon
                  icon="i-carbon-chevron-left"
                  outlined
                  color="primary"
                  tooltip="Página Anterior"
                  :disabled="onFirstEndedPage"
                  class="rounded-r-0"
                  @click="goPreviousEndedPage"
                />
                <BtnIcon
                  icon="i-carbon-chevron-right"
                  outlined
                  color="primary"
                  tooltip="Próxima Página"
                  :disabled="onLastEndedPage"
                  class="rounded-l-0 border-l-0"
                  @click="goNextEndedPage"
                />
              </div>
            </div>
            <div class="text-3">
              Página {{ endedPagination.page }} de {{ endedPagination.rowsNumber ?? 0 }}
            </div>
          </div>

          <div v-if="endedVotings?.length" v-auto-animate>
            <div
              v-for="votingData in endedVotings"
              :key="votingData.id"
              class="p-2 hover:bg--secondary/20 rounded cursor-pointer mb-2 flex gap-2 items-center"
              :class="{
                'hover:bg--error/20!': votingData.id === voting.id,
              }"
              @click="runVoting(votingData.id === voting.id ? 'finish' : 'start', votingData)"
            >
              <div
                class="flex-1"
                :class="{
                  'font-bold': votingData.id === voting.id,
                }"
              >
                <div>{{ votingData.description }}</div>
                <div class="flex gap-2 items-center">
                  <div class="px-2 py-.5 bg-gray/20 text-3 rounded-full">
                    {{ votingData.typeDisplay }}
                  </div>
                  <div
                    class="px-2 py-.5 rounded-full text-white text-3"
                    :style="{
                      background: votingData.statusColor,
                    }"
                  >
                    {{ votingData.statusDisplay }}
                  </div>
                </div>
              </div>
              <div v-if="votingData.id !== voting.id" class="i-carbon-play-filled-alt text--secondary" />
              <div v-else class="i-carbon-stop-filled-alt text--error" />
            </div>
          </div>
          <div v-else class="px-2 py-4 color-gray-5">
            Nenhuma Votação Finalizada encontrada...
          </div>
        </Expandable>
      </div>
    </div>

    <NewVoting
      v-model:open="showNewVoting"
      :meeting-id="meetingId"
    />
    <RunVoting
      v-model:open="showRunVoting"
      :voting="selectedVoting"
      :type="runVotingType"
    />
  </Drawer>
</template>