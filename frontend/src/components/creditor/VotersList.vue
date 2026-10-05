<script setup>
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
    required: true,
  },
})
const emit = defineEmits(['update:open', 'update:loading', 'click'])

const { isMobile } = useAmbient()
const { dialog } = useQuasar()
const activeList = $ref('creditors') // or 'representatives'

const meeting = $computed(() => props.socket.channels.meetingDetail ?? {})
const voting = $computed(() => props.socket.channels.votingProgress ?? {})
watch(()=> voting.id, (votingId)=> {
  if(votingId)
    meetingRepresentatives.updatePagination({ votingId })
})

const activeVoter = $computed(() => activeList === 'creditors' ? 'Credor' : 'Representante')
const totalVoters = $computed(() => meeting?.[activeList === 'creditors' ? 'countCreditors' : 'countRepresentatives'] ?? 0)

const onPresence = $computed(() => meeting?.ableToRegisterPresence && !voting?.id)
const classesNames = $computed(() => ([
  ...new Set(((voting.classChoice ?? meeting.creditorsCredit) ?? [])
    .map((classe) => voting.classChoice ? classe.classe : classe.name)
    .sort())
]))

const choices = $computed(() => voting?.classChoice ?? [])
const sortedChoices = $computed(() => choices?.[0]?.choices?.map(({ value }) => value) ?? [])
const useChoices = $computed(() => {
  const localChoices = choices.reduce((acc, { choices, classe }) => {
    choices.forEach((choice) => {
      const { value } = choice
      if (!acc[value])
        acc[value] = {}
      acc[value][classe] = choice.id
    })
    return acc
  }, {})
  return sortedChoices?.map(value => ({
    value,
    choices: localChoices[value],
  })) ?? []
})

const onLoad = {
  start: () => emit('update:loading', true),
  end: () => emit('update:loading', false),
}
const creditors = meetingService
  .getCreditors(props.meetingId, props.socket)
creditors.onLoad(onLoad)
creditors.updatePagination({ classes: {}, voted: false, notVoted: false })

const meetingRepresentatives = meetingService
  .getRepresentatives(props.meetingId, props.socket)
meetingRepresentatives.onLoad(onLoad)
meetingRepresentatives.updatePagination({ classes: {}, voted: false, notVoted: false })

const list = $computed(() => activeList === 'creditors' ? creditors : meetingRepresentatives)
const pagination = $computed(() => list.pagination.value ?? {})
const items = $computed(() => list.items.value ?? [])

function toggleVoted(voted) {
  const flag = voted ? 'voted' : 'notVoted'
  const unflag = voted ? 'notVoted' : 'voted'
  list.updatePagination({
    [flag]: !pagination[flag] ? voting.id : undefined,
    [unflag]: undefined,
    page: 1,
  })
}

function toggleClasseName(name) {
  list.updatePagination({
    classes: {
      ...pagination.classes,
      [name]: !(pagination.classes?.[name] ?? false),
    },
    page: 1,
  })
}

let showVotingByCreditor = $ref(false)
let showVotingByRepresentative = $ref(false)
let selectedVoter = $ref({})

function selectVoter(voter) {
  if (!onPresence && !voting.id)
    return

  if (onPresence && voter?.presence?.isAccredited) {
    throwError({ message: 'Essa pessoa já se credenciou!' })
    return
  }

  if (onPresence) {
    registerPresence(voter)
    return
  }

  // Verificar credenciamento para representantes
  if (voting.id && voter.isRepresentative && !(voter?.allCreditorsAccredited && voter?.isAccredited)) {
    throwError({ message: 'Esse Representante não se credenciou!' })
    return
  }
  // Verificar credenciamento para credores
  if(voting.id && !voter.isRepresentative && !voter.isAccredited) {
    throwError({ message: 'Esse Credor não se credenciou!' })
    return
  }

  if (voter?.votingIds?.includes(voting.id)) {
    throwError({ message: 'Essa pessoa já votou!' })
    return
  }

  if (!voter.isRepresentative && !classesNames
    .map(classe => classe.toLowerCase())
    .includes(voter?.classe?.description?.toLowerCase())
  ) {
    throwError({ message: 'Esse Credor não está nesta votação!' })
    return
  }

  if (voter.isRepresentative) {
    showVotingByRepresentative = true
    selectedVoter = voter
    return
  }

  showVotingByCreditor = true
  selectedVoter = voter
}

async function registerPresence(voter) {
  dialog({
    title: 'Registrando Presença',
    message: 'Você tem certeza que esta pessoa está ciente desta ação?',
    cancel: true,
    persistent: true,
  })
    .onOk(async () => {
      onLoad.start()
      try {
        const result = await presenceService.registerVoterPresence(voter)
        if (result.id)
          notify({ message: 'A presença foi registrada com sucesso!' })
      }
      catch (error) {
        print('ERROR ON REGISTRING VOTER PRESENCE ON LIVE:', error)
      }
      finally {
        onLoad.end()
      }
    })
}

onMounted(() => {
  list.get()
})
</script>

<template>
  <Drawer
    :open="open"
    title="Participantes"
    position="right"
    class="border-l-1 border--content/12"
    @click="emit('click')"
  >
    <div class="w-80 flex-1 flex flex-col h-full">
      <div class="pl-2">
        <QTabs
          v-model="activeList"
          align="left"
          active-color="primary"
          dense
        >
          <QTab
            name="creditors"
            label="Credores"
          />
          <QTab
            name="representatives"
            label="Representantes"
          />
        </QTabs>
        <div class="flex flex-nowrap gap-2 py-2 pr-2">
          <BtnIcon
            icon="i-carbon-renew"
            outlined
            color="primary"
            tooltip="Recarregar Lista"
            @click="() => list.get()"
          />
          <div class="flex flex-nowrap">
            <BtnIcon
              icon="i-carbon-chevron-left"
              outlined
              color="primary"
              tooltip="Página Anterior"
              :disabled="list.onFirstPage.value"
              class="rounded-r-0"
              @click="list.previousPage"
            />
            <BtnIcon
              icon="i-carbon-chevron-right"
              outlined
              color="primary"
              tooltip="Próxima Página"
              :disabled="list.onLastPage.value"
              class="rounded-l-0 border-l-0"
              @click="list.nextPage"
            />
          </div>
          <SearchFilter
            class="flex-1"
            @update:search="list.updatePagination({ filterBy: $event, page: 1 })"
          />
        </div>
        <div class="text-3 text-right pr-2">
          <div class="flex gap-1">
            <button
              v-for="(name, i) in classesNames"
              :key="i"
              class="py-.6 px-2 font-bold bg-gray/20 rounded-full text-2.5 whitespace-nowrap text-ellipsis overflow-hidden"
              :class="{
                'bg--primary text-white': pagination?.classes?.[name],
              }"
              @click="toggleClasseName(name)"
            >
              {{ name }}
            </button>
            <button
              v-if="voting.id"
              class="py-.6 px-2 font-bold bg-gray/20 rounded-full text-2.5 whitespace-nowrap text-ellipsis overflow-hidden"
              :class="{
                'bg--primary text-white': pagination?.voted,
              }"
              @click="toggleVoted(true)"
            >
              Votou
            </button>
            <button
              v-if="voting.id"
              class="py-.6 px-2 font-bold bg-gray/20 rounded-full text-2.5"
              :class="{
                'bg--primary text-white': pagination?.notVoted,
              }"
              @click="toggleVoted(false)"
            >
              Não Votou
            </button>
          </div>
          <div class="flex justify-between gap-2 py-1">
            <div>página: {{ pagination?.page ?? 0 }} de {{ Math.ceil((pagination.rowsNumber ?? 0) / (pagination.rowsPerPage || 1)) }}</div>
            <div>Credores: {{ pagination?.rowsNumber ?? 0 }} de {{ totalVoters }}</div>
          </div>
        </div>
      </div>
      <div v-if="totalVoters > 0" class="flex-1 overflow-y-auto overflow-x-hidden pr-2 pt-2">
        <div v-if="items?.length > 0" v-auto-animate>
          <div
            v-for="voter in items"
            :key="voter.id"
            class="p-2 hover:bg--secondary/20 rounded cursor-pointer mb-2"
            @click="selectVoter(voter)"
          >
            <div class="flex gap-2">
              <div class="flex-1 font-bold">
                {{ voter?.guest?.user?.firstName }} {{ voter?.guest?.user?.lastName }}
              </div>
              <div
                v-if="voter?.isAccredited"
                class="h-2 w-2 bg--primary rounded-full"
              >
                <QTooltip
                  v-if="!isMobile()"
                  anchor="center left"
                  self="top right"
                >
                  {{ activeVoter }} já se credenciou!
                </QTooltip>
              </div>
              <div
                v-if="voting?.id && (voter?.bigNumbers?.countNotVoted <=0 && voter?.isAccredited) || voter?.votingIds?.includes(voting.id)"
                class="h-2 w-2 bg--secondary rounded-full"
              >
                <QTooltip
                  v-if="!isMobile()"
                  anchor="center left"
                  self="top right"
                >
                  {{ activeVoter }} já votou!
                </QTooltip>
              </div>
              <div v-else-if="voting?.id" class="h-2 w-2 bg-orange rounded-full">
                <QTooltip
                  v-if="!isMobile()"
                  anchor="center left"
                  self="top right"
                >
                  {{ activeVoter === 'Credor' ? 'Credor ainda não votou...' : `${voter?.bigNumbers?.countNotVoted ?? 0} credores ainda não votaram...` }}
                </QTooltip>
              </div>
            </div>
            <div class="flex items-center justify-between">
              <div>{{ formatLegalNumber(voter?.guest?.entity.legalNumber) }}</div>
              <div v-if="voter?.classe?.description" class="px-2 py-.5 bg-gray/20 text-3 rounded-full max-w-35 whitespace-nowrap text-ellipsis overflow-hidden">
                {{ voter?.classe?.description }}
              </div>
            </div>
          </div>
        </div>
        <div v-else class="color-gray-5 p-4 flex-1 flex justify-center items-center text-center">
          Nenhum {{ activeVoter }} encontrado...
        </div>
      </div>
      <div v-else class="p-4 flex-1 flex justify-center items-center text-center">
        Nenhum {{ activeVoter }} cadastrado
      </div>
    </div>
    <VotingByCreditor
      v-model:open="showVotingByCreditor"
      :creditor="selectedVoter"
      :choices="useChoices"
    />
    <VotingByRepresentative
      v-model:open="showVotingByRepresentative"
      :representative="selectedVoter"
      :voting="voting"
      @close="() => meetingRepresentatives.get()"
    />
  </Drawer>
</template>