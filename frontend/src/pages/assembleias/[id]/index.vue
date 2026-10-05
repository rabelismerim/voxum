<script setup>
const { dialog } = useQuasar()
const attrs = useAttrs()
const router = useRouter()

const { login, hasPermissions } = useUser
const { isMobile } = useAmbient()
const { loadLocations } = useLocations()

let loading = $ref(false)
let showExportReports = $ref(false)
const filterBy = $ref('')

const showEditMeeting = $ref(false)
const showNewRepresentative = $ref(false)
let showDetailVoting = $ref(false)

const selectedTab = $ref('creditors')
const tabs = [
  { label: 'Credores', value: 'creditors' },
  { label: 'Representantes', value: 'representatives' },
  { label: 'Credenciamento', value: 'presence' },
  { label: 'Votações', value: 'votings' },
]

const meetingStatusColors = {
  I: '#007db3', // iniciada
  E: '#007cb0', // encerrada
  A: '#cccccc', // Agendada
  T: '#DA291C', // atrasada
  R: '#FFD700', // reagendada
}
const votingStatus = {
  I: 'Iniciada',
  A: 'Agendada',
  E: 'Encerrada',
  R: 'Reagendada',
}
const votingStatusColors = {
  I: '#007db3', // iniciada
  A: '#cccccc', // Agendada
  E: '#007cb0', // encerrada
  R: '#FFD700', // reagendada
}

let options = $ref({})
async function loadOptions() {
  try {
    options = await meetingService.getMeetingOptions()
  }
  catch (error) {
    print('ERROR ON LOADING NEW VOTING OPTIONS:', error)
  }
}

let isEditing = $ref(false)
let editingCreditor = $ref({})
function editCreditor(creditor) {
  isEditing = true
  editingCreditor = creditor
}

let isEditingRepresentative = $ref(false)
let editingRepresentative = $ref({})
function editRepresentative(representative) {
  isEditingRepresentative = true
  editingRepresentative = representative
}

let localBigNumbers = $ref({})
async function loadBigNumbers() {
  try {
    localBigNumbers = await meetingService.getBigNumbers(attrs.id)
  }
  catch (error) {
    print('ERROR ON LOADING BIGNUMBERS:', error)
  }
}

const showUploadCreditors = $ref(false)

const { socket, open, remove: removeSocket } = useSocket({ url: `V1/meetings/${attrs.id}` })

let initialMeeting = $ref({})
const meeting = $computed(() => socket.value.channels.meetingDetail ?? initialMeeting)
const meetingName = $computed(() => `Assembleia: ${meeting.name ?? ''}`)
const totalValue = $computed(() => meeting?.totalCredit ?? localBigNumbers?.totalCredit ?? 0)
const hasAccredited = $computed(() => meeting.situation == 3 || !meeting?.ableToRegisterPresence && meeting?.startRegisterPresence)

const backendNotification = $computed(() => socket.value.channels?.notificationToast ?? {})
watch(() => backendNotification, notification => {
  if (notification?.data?.message) notify(notification.data)
})

const {
  pagination: creditorsPagination,
  updatePagination: updateCreditorsPagination,
  items: creditors,
  get: loadCreditors,
  loading: loadingCreditors,
} = meetingService.getCreditors(attrs.id, socket)
updateCreditorsPagination?.({ filterColumn: 'first_name' })
const creditorsCount = $computed(() => meeting?.countCreditors ?? creditorsPagination?.value?.rowsNumber ?? 0)

const {
  pagination: representativesPagination,
  updatePagination: updateRepresentativesPagination,
  items: representatives,
  get: loadRepresentatives,
  loading: loadingRepresentatives,
} = meetingService.getRepresentatives(attrs.id, socket)
updateRepresentativesPagination?.({ filterColumn: 'first_name' })
const representativesCount = $computed(() => meeting?.countRepresentatives ?? representativesPagination?.value?.rowsNumber ?? 0)

const {
  pagination: votingsPagination,
  updatePagination: updateVotingsPagination,
  items: votings,
  get: loadVotings,
  loading: loadingVotings,
} = votingService.getVotings(attrs.id, socket)
updateVotingsPagination?.({ filterColumn: 'description' })

const showNewVoting = $ref(false)
let showRunVoting = $ref(false)
let selectedVoting = $ref({})
function selectVoting(voting) {
  showRunVoting = true
  selectedVoting = voting
}

function detailVoting(voting) {
  showDetailVoting = true
  selectedVoting = voting
}

async function endVoting(voting) {
  loading = true
  try {
    await votingService.finish(voting.id)
    notify({ message: 'Votação encerrada com sucesso!' })
  }
  catch (error) {
    print('ERROR ON ENDING MEETING ON ADMIN:', error)
  }
  finally {
    loading = false
  }
}
async function deleteVoting(voting) {
  dialog({
    title: 'Apagando Votação',
    message: 'Você tem certeza que deseja apagar esta Votação?',
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    loading = true
    try {
      const result = await votingService.remove(voting)
      if (!result)
        return
      notify({
        message: 'Votação removida com sucesso!',
      })
    }
    catch (error) {
      print('ERROR ON DELETING VOTING:', error)
    }
    finally {
      loading = false
    }
  })
}

async function startMeeting() {
  if(meeting.id && meeting.situation != 3) {
    showRunPresence = true
    return
  }

  loading = true
  try {
    await meetingService.updateMeeting({id: attrs.id, status: 'I'})
  }
  catch (error) {
    print('ERROR ON STARTING MEETING:', error)
  }
  finally {
    loading = false
  }
}
async function endMeeting() {
  dialog({
    title: 'Encerrar Assembleia',
    message: 'Você tem certeza que deseja encerrar esta Assembleia?',
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    loading = true;
    try {
      const result = await meetingService.updateMeeting({
        ...meeting,
        status: 'E',
      });

      if (!result) {
        notify({
          message: 'Falha ao encerrar a Assembleia!',
        });
        return;
      }

      notify({
        message: 'Assembleia encerrada com sucesso!',
      });
    } catch (error) {
      print('ERROR ON ENDING MEETING:', error);
    } finally {
      loading = false;
    }
  });
}

async function deleteCreditor(creditor) {
  dialog({
    title: 'Apagando Credor',
    message: 'Você tem certeza que deseja apagar este Credor?',
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    loading = true
    const creditorId = typeof creditor === 'object' && creditor !== null ? creditor.id : creditor

    try {
      if (!creditorId)
        throw new Error('Credor ID não encontrado.')

      const result = await creditorsService.deleteCreditor(creditorId)
      if (!result)
        return
      notify({ message: 'Credor removido com sucesso!' })
    }
    catch (error) {
      print('ERROR ON DELETING CREDITOR:', error)
    }
    finally {
      loading = false
    }
  })
}

let showPresenceDetail = $ref(false)
let showPresenceGraph = $ref(false)
let showRunPresence = $ref(false)
const onPresence = $computed(() => meeting.ableToRegisterPresence)
const presenceStatus = $computed(() => {
  if (!meeting.startRegisterPresence || !meeting.endRegisterPresence)
    return 'Não Iniciado'
  if (onPresence)
    return 'Em Andamento'
  return 'Finalizado'
})

const presenceData = $computed(() => [{
  description: 'Credenciamento',
  startDate: meeting.startRegisterPresence,
  endDate: meeting.endRegisterPresence,
  creditors: meeting?.countCreditors ?? 0,
  presenceCount: meeting?.creditorsPresenceStatus?.reduce((acc, { countAccredited }) => acc + countAccredited, 0),
  status: presenceStatus,
}])
async function endPresence() {
  loading = true
  try {
    await presenceService.finish(meeting.id)
    notify({ message: 'Credenciamento encerrado com sucesso!' })
  }
  catch (error) {
    print('ERROR ON ENDING PRESENCE ON ADMIN:', error)
  }
  finally {
    loading = false
  }
}

const graphResult = $ref({
  show: false,
  selected: null,
})
function showGraphResult(voting) {
  graphResult.show = true
  graphResult.selected = voting
}
function exportVotingReports(voting) {
  showExportReports = true
  selectedVoting = voting
}

let sendingEmail = $ref(false)
async function sendRegister() {
  sendingEmail = true
  try {
    const {status} = await meetingService.sendRegisterEmail(meeting.id)
    if(status === 'ok')
      notify({message: 'E-mail de cadastro enviado com sucesso!'})
  }
  catch(error) {
    print('ERROR ON SENDING REGISTER EMAIL:', error)
  }
  finally {
    sendingEmail = false
  }
}
async function sendAccess() {
  sendingEmail = true
  try {
    const {status} = await meetingService.sendAccessEmail(meeting.id)
    if(status === 'ok')
      notify({message: 'E-mail de acesso enviado com sucesso!'})
  }
  catch(error) {
    print('ERROR ON SENDING REGISTER EMAIL:', error)
  }
  finally {
    sendingEmail = false
  }
}

const reduceCountBy = (list, key) => list.reduce((acc, curr) => curr[key] + acc, 0)
const creditorsColumns = [
  {
    name: 'first_name',
    field: 'fullName',
    label: 'Nome',
    align: 'left',
    sortable: true,
    format: value => value ?? '-',
  },
  {
    name: 'legal_number',
    field: 'legalNumber',
    label: 'Documento',
    align: 'left',
    sortable: true,
    format: value => formatLegalNumber(value) ?? '-',
  },
  {
    name: 'email',
    field: 'guest',
    label: 'E-mail',
    align: 'left',
    sortable: true,
    format: value => value?.user?.email ?? '-',
  },
  {
    name: 'classe',
    field: 'classe',
    label: 'Classe',
    align: 'left',
    sortable: true,
    format: value => value?.description ?? '-',
  },
  {
    name: 'credit_value',
    field: 'creditValue',
    label: 'Valor',
    align: 'left',
    sortable: true,
    format: (value, row) => formatMoney(value, row?.coin?.typeDisplay),
  },
  {
    name: 'representatives',
    field: 'representatives',
    label: 'Representantes',
    align: 'left',
    format: value => value?.length ? value?.map(e => e?.fullName ?? '')?.join(', ') : '-',
  },
  {
    name: 'doc',
    field: 'docOk',
    label: 'Documento',
    align: 'left',
    sortable: true,
    format: value => value ? '✔️' : '-',
  },
  {
    name: 'is_accredited',
    field: 'presence',
    label: 'Credenciado',
    align: 'left',
    sortable: true,
    format: value => value?.isAccredited ? '✔️' : '-',
  },
  {
    name: 'online',
    field: 'online',
    label: 'Online',
    align: 'left',
    sortable: true,
    format: value => value ? '🔵' : '🔴',
  },
  {
    name: 'arrival_date',
    field: 'presence',
    label: 'Chegada',
    align: 'left',
    sortable: true,
    format: value => formatDate(value?.arrivalDate, '@DD/@MM/@YYYY @HH:@mm:@ss', '-'),
  },
  {
    name: 'departure_date',
    field: 'presence',
    label: 'Saída',
    align: 'left',
    sortable: true,
    format: value => formatDate(value?.departureDate, '@DD/@MM/@YYYY @HH:@mm:@ss', '-'),
  },
  {
    name: 'extra',
    field: 'extra',
    label: 'Ações',
  },
]
const representativesColumns = [
  {
    name: 'first_name',
    field: 'fullName',
    label: 'Nome',
    sortable: true,
    align: 'left',
    format: value => value ?? '-',
  },
  {
    name: 'legal_number',
    field: 'legalNumber',
    label: 'Documento',
    align: 'left',
    sortable: true,
    format: value => formatLegalNumber(value) ?? '-',
  },
  {
    name: 'email',
    field: 'guest',
    label: 'E-mail',
    sortable: true,
    align: 'left',
    format: value => `${value?.user?.email}`,
  },
  {
    name: 'doc',
    field: 'docOk',
    label: 'Documento',
    align: 'left',
    sortable: true,
    format: value => value ? '✔️' : '-',
  },
  {
    name: 'is_accredited',
    field: 'isAccredited',
    label: 'Credenciado',
    align: 'left',
    sortable: true,
    format: value => value ? '✔️' : '-',
  },
  {
    name: 'online',
    field: 'online',
    label: 'Online',
    align: 'left',
    sortable: true,
    format: value => value ? '🔵' : '🔴',
  },
  {
    name: 'arrival_date',
    field: 'presence',
    label: 'Chegada',
    align: 'left',
    sortable: true,
    format: value => formatDate(value?.arrivalDate, '@DD/@MM/@YYYY @HH:@mm:@ss', '-'),
  },
  {
    name: 'departure_date',
    field: 'presence',
    label: 'Saída',
    align: 'left',
    sortable: true,
    format: value => formatDate(value?.departureDate, '@DD/@MM/@YYYY @HH:@mm:@ss', '-'),
  },
]
const votingsColumns = [
  {
    name: 'description',
    field: 'description',
    label: 'Pergunta',
    align: 'left',
    sortable: true,
  },
  {
    name: 'type',
    field: 'typeDisplay',
    label: 'Tipo',
    align: 'left',
    sortable: true,
  },
  {
    name: 'classes',
    field: 'classChoice',
    label: 'Classes',
    align: 'left',
    format: value => value?.length ? value.map(({ classe: name }) => name).sort().join(', ') : '-',
  },
  {
    name: 'start_date',
    field: 'startDate',
    label: 'Data Início',
    align: 'left',
    sortable: true,
    format: value => formatDate(value, '@DD/@MM/@YYYY @HH:@mm:@ss', '-'),
  },
  {
    name: 'end_date',
    field: 'endDate',
    label: 'Data Encerramento',
    align: 'left',
    sortable: true,
    format: value => formatDate(value, '@DD/@MM/@YYYY @HH:@mm:@ss', '-'),
  },
  {
    name: 'progress',
    field: 'results',
    label: 'Progresso',
    align: 'left',
    format: value => (reduceCountBy(value, 'countVoters') / reduceCountBy(value, 'countQualifiedCreditors')) * 100 ?? 0,
  },
  {
    name: 'status',
    field: 'status',
    label: 'Status',
    sortable: true,
    align: 'right',
  },
  {
    name: 'action',
    field: 'action',
    label: 'Executar',
  },
  {
    name: 'extra',
    field: 'extra',
    label: 'Ações',
  },
]
const presenceColumns = [
  {
    name: 'description',
    field: 'description',
    label: 'Descrição',
    align: 'left',
    sortable: true,
  },
  {
    name: 'start_date',
    field: 'startDate',
    label: 'Data Início',
    align: 'left',
    sortable: true,
    format: value => formatDate(value, '@DD/@MM/@YYYY @HH:@mm:@ss', '-'),
  },
  {
    name: 'end_date',
    field: 'endDate',
    label: 'Data Encerramento',
    align: 'left',
    sortable: true,
    format: value => formatDate(value, '@DD/@MM/@YYYY @HH:@mm:@ss', '-'),
  },
  {
    name: 'progress',
    field: 'presenceCount',
    label: 'Progresso',
    align: 'left',
    sortable: true,
  },
  {
    name: 'status',
    field: 'status',
    label: 'Status',
    sortable: true,
    align: 'right',
  },
  {
    name: 'action',
    field: 'action',
    label: 'Executar',
  },
  {
    name: 'extra',
    field: 'extra',
    label: 'Ações',
  },
]

const isLoading = $computed(() => loading || loadingCreditors?.value || loadingRepresentatives?.value || loadingVotings?.value || sendingEmail)
onMounted(async () => {
  if (attrs.id === 'undefined') {
    router.push('/assembleias')
    return
  }
  login()
  meetingService.getMeeting(attrs.id)
    .then(result => initialMeeting = result)
    .catch(error => print('ERROR ON LOADING MEETING DETAILS:', error))
  loadBigNumbers()
  loadOptions()
  loadLocations().catch(error => print('ERROR ON LOAD LOCATIONS:', error))
  loadCreditors()
  loadRepresentatives()
  loadVotings()
})
onBeforeUnmount(() => {
  removeSocket()
})
</script>

<template>
  <Page :loading="isLoading">
    <div class="px-4 w-full md:w-94% max-w-400 min-w-60 mx-auto py-8">
      <Header
        :title="meetingName"
        class="mb-4"
      >
        <template #subtitle>
          <div class="flex flex-col gap-2 mt-2">
            <div class="flex flex-wrap gap-2 items-center">
              <StatusTag
                v-if="meeting.status"
                :label="meeting.statusDisplay"
                :color="meetingStatusColors[meeting.status]"
              />
              <StatusTag
                v-if="meeting.situationDisplay"
                :label="meeting.situationDisplay"
              />
              <SocketTag
                :socket="socket"
                @click="open"
              />
            </div>
            <div v-if="meeting.description">
              <span class="font-bold mr-1">Descrição:</span>{{ meeting.description }}
            </div>
          </div>
        </template>
      </Header>

      <div class="grid md:grid-cols-3 gap-3 mb-4">
        <GraphCard
          title="Quant. de Credores"
          tooltip="Credores que estão listados nesta Assembleia"
        >
          <div class="font-bold text-3xl">
            {{ creditorsCount }}
          </div>
        </GraphCard>
        <GraphCard
          title="Quant. de Representantes"
          tooltip="Representantes que estão listados nesta Assembleia"
        >
          <div class="font-bold text-3xl">
            {{ representativesCount }}
          </div>
        </GraphCard>
        <GraphCard
          title="Valor Total"
          tooltip="Valor de todos os créditos listados nesta Assembleia"
        >
          <div class="font-bold text-3xl">
            {{ formatMoney(totalValue) }}
          </div>
        </GraphCard>
      </div>

      <TabFilter
        v-model="selectedTab"
        :items="tabs"
      >
        <SearchFilter
          v-if="selectedTab === 'creditors'"
          v-model:search="creditorsPagination.filterBy"
          v-model:field="creditorsPagination.filterColumn"
          auto-size
          class="my-1.5"
          :options="{
            first_name: 'Nome do Credor',
            legal_number: 'CPF/CNPJ',
          }"
        />
        <SearchFilter
          v-else-if="selectedTab === 'representatives'"
          v-model:search="representativesPagination.filterBy"
          v-model:field="representativesPagination.filterColumn"
          auto-size
          :options="{
            first_name: 'Nome do Representante',
            legal_number: 'CPF/CNPJ',
          }"
        />
        <SearchFilter
          v-else-if="selectedTab === 'votings'"
          v-model:search="votingsPagination.filterBy"
          v-model:field="votingsPagination.filterColumn"
          :options="{
            description: 'Pergunta',
            type: 'Tipo',
            status: 'Status',
          }"
        />
      </TabFilter>

      <QTabPanels v-model="selectedTab" keep-alive>
        <QTabPanel name="creditors">
          <QTable
            v-model:pagination="creditorsPagination"
            :rows="creditors"
            :columns="creditorsColumns"
            :filter="filterBy"
            :no-data-label="isLoading ? 'carregando...' : 'Nenhum credor listado'"
            :rows-per-page-options="[5, 10, 15, 20, 25]"
            row-key="id"
            flat
            bordered
            @row-click="(_, row) => editCreditor(row)"
            @request="updateCreditorsPagination($event?.pagination)"
          >
            <template #top>
              <div class="flex w-full justify-between items-center gap-3 mt-1 md:mt-0  min-h-11">
                <div class="flex gap-2 items-center">
                  <h2 class="font-bold text-7 leading-6">
                    {{ creditorsCount }} Credor{{ creditors?.length < 2 ? '' : 'es' }} Ativo{{ creditorsCount < 2 ? '' : 's' }}
                  </h2>
                  <ReloadBtn
                    tooltip="Recarregar lista de credores"
                    @click="loadCreditors"
                  />
                </div>
                <div v-if="meeting.id" class="flex gap-3">
                  <Btn
                    label="Enviar Cadastro"
                    tooltip="Enviar e-mail de cadastro para todos os credores"
                    outlined
                    :disabled="!meeting.id"
                    @click="sendRegister"
                  />
                  <Btn
                    label="Enviar Acesso"
                    tooltip="Enviar e-mail de acesso à Assembléia para todos os credores"
                    outlined
                    :disabled="!meeting.id"
                    @click="sendAccess"
                  />
                  <Btn
                    label="Importar Credores"
                    icon="i-carbon-user-follow"
                    tooltip="Importar lista de credores com planilha Excel"
                    :disabled="!meeting.id"
                    @click="showUploadCreditors = true"
                  />
                </div>
              </div>
            </template>
            <template #body-cell-representatives="{ value, row }">
              <QTd>
                <div class="max-w-60 text-ellipsis overflow-hidden">
                  {{ value }}
                </div>
                <QTooltip v-if="row.representatives?.length && !isMobile()">
                  <ul class="list-disc">
                    <li
                      v-for="item in row.representatives"
                      :key="item.id"
                    >
                      • {{ item.fullName ?? '-' }}
                    </li>
                  </ul>
                </QTooltip>
              </QTd>
            </template>
            <template #body-cell-extra="{ row }">
              <QTd>
                <div class="flex justify-end">
                  <BtnIcon
                    flat
                    color="primary"
                    icon="i-carbon-overflow-menu-vertical"
                    class="rounded-full"
                    @click.stop
                  >
                    <QMenu>
                      <QList class="min-w-30">
                        <QItem
                          v-if="hasPermissions('can_manage_project')"
                          v-close-popup
                          clickable
                          @click="editCreditor(row)"
                        >
                          <QItemSection>
                            Editar Credor
                          </QItemSection>
                        </QItem>
                        <QItem
                          v-if="hasPermissions('can_manage_project')"
                          v-close-popup
                          clickable
                          class="color--negative"
                          @click="deleteCreditor(row)"
                        >
                          <QItemSection>
                            Excluir Credor
                          </QItemSection>
                        </QItem>
                      </QList>
                    </QMenu>
                  </BtnIcon>
                </div>
              </QTd>
            </template>
          </QTable>
          <q-dialog v-model="dialog.open">
            <q-card>
              <q-card-section>
                Tem certeza que deseja excluir este credor?
              </q-card-section>
              <q-card-actions>
                <q-btn
                  flat
                  label="Cancelar"
                  color="primary"
                  @click="dialog.open = false"
                />
                <q-btn
                  flat
                  label="Excluir"
                  color="negative"
                  @click="confirmDelete"
                />
              </q-card-actions>
            </q-card>
          </q-dialog>
        </QTabPanel>
        <QTabPanel name="representatives">
          <QTable
            v-model:pagination="representativesPagination"
            :rows="representatives"
            :columns="representativesColumns"
            :no-data-label="isLoading ? 'carregando...' : 'Nenhum Representante listado'"
            :filter="filterBy"
            row-key="id"
            :rows-per-page-options="[5, 10, 15, 20, 25]"
            flat
            bordered
            @request="updateRepresentativesPagination($event?.pagination)"
            @row-click="(_, row) => editRepresentative(row)"
          >
            <template #top>
              <div class="flex w-full justify-between items-center gap-3 mt-1 md:mt-0  min-h-11">
                <div class="flex gap-2 items-center">
                  <h2 class="font-bold text-7 leading-6">
                    {{ representativesCount }} Representante{{ representatives?.length < 2 ? '' : 's' }} Ativo{{ representatives?.length < 2 ? '' : 's' }}
                  </h2>
                  <ReloadBtn
                    tooltip="Recarregar lista de Representantes"
                    @click="loadRepresentatives"
                  />
                </div>
                <Btn
                  v-if="meeting.id"
                  label="Cadastrar Representante"
                  tooltip="Cadastrar novo representante"
                  icon="i-carbon-user-follow"
                  @click="showNewRepresentative = true"
                />
              </div>
            </template>
          </QTable>
        </QTabPanel>
        <QTabPanel name="votings">
          <QTable
            v-model:pagination="votingsPagination"
            :rows="votings"
            :columns="votingsColumns"
            :filter="filterBy"
            :rows-per-page-options="[5, 10, 15, 20, 25]"
            :no-data-label="isLoading ? 'carregando...' : 'Nenhuma Votação listada'"
            row-key="id"
            flat
            bordered
            @request="updateVotingsPagination($event?.pagination)"
            @row-click="(_, row) => detailVoting(row)"
          >
            <template #top>
              <div class="flex w-full justify-between items-center gap-3 mt-1 md:mt-0  min-h-11">
                <div class="flex gap-2 items-center">
                  <h2 class="font-bold text-7 leading-6">
                    {{ votings?.length }} Votaç{{ votings?.length < 2 ? 'ão' : 'ões' }}
                  </h2>
                  <ReloadBtn
                    tooltip="Recarregar lista de Votações"
                    @click="loadVotings"
                  />
                </div>
                <Btn
                  v-if="meeting.id"
                  label="Nova Votação"
                  tooltip="Cadastrar nova votação"
                  icon="i-carbon-add-filled"
                  @click="showNewVoting = true"
                />
              </div>
            </template>
            <template #body-cell-progress="{ value, row }">
              <QTd>
                <Progress
                  :percentage="value || 0"
                  :tooltip="row.results?.length ? `${reduceCountBy(row.results, 'countVoters') || 0} de ${reduceCountBy(row.results, 'countQualifiedCreditors') || 0}` : ''"
                />
              </QTd>
            </template>
            <template #body-cell-status="{ value }">
              <QTd>
                <div class="flex justify-end">
                  <StatusTag :label="votingStatus[value]" :color="votingStatusColors[value]" />
                </div>
              </QTd>
            </template>
            <template #body-cell-action="{ row }">
              <QTd>
                <div class="flex justify-end">
                  <BtnIcon
                    v-if="row.status !== 'I'"
                    icon="i-carbon-play-filled-alt"
                    class="rounded-full"
                    :tooltip="!hasAccredited ? 'Inicie o Credenciamento antes da Votação' : 'Iniciar Votação'"
                    :disabled="votings?.some(voting => voting.status === 'I') || !hasAccredited"
                    @click.stop="selectVoting(row)"
                  />
                  <BtnIcon
                    v-else
                    icon="i-carbon-stop-filled-alt"
                    color="error"
                    class="rounded-full"
                    tooltip="Encerrar Votação"
                    :disabled="!!meeting.ableToRegisterPresence"
                    @click.stop="endVoting(row)"
                  />
                </div>
              </QTd>
            </template>
            <template #body-cell-extra="{ row }">
              <QTd>
                <div class="flex justify-end">
                  <BtnIcon
                    flat
                    color="primary"
                    icon="i-carbon-overflow-menu-vertical"
                    class="rounded-full"
                    @click.stop
                  >
                    <QMenu>
                      <QList class="min-w-35">
                        <QItem
                          v-close-popup
                          clickable
                          @click="detailVoting(row)"
                        >
                          <QItemSection>
                            Detalhe da Votação
                          </QItemSection>
                        </QItem>
                        <QItem
                          v-close-popup
                          clickable
                          @click="showGraphResult(row)"
                        >
                          <QItemSection>
                            Exportar Gráficos
                          </QItemSection>
                        </QItem>
                        <QItem
                          v-close-popup
                          clickable
                          @click="exportVotingReports(row)"
                        >
                          <QItemSection>
                            Exportar Relatórios
                          </QItemSection>
                        </QItem>
                        <QItem
                          v-if="hasPermissions('can_manage_project')"
                          v-close-popup
                          clickable
                          class="color--negative"
                          @click="deleteVoting(row)"
                        >
                          <QItemSection>
                            Apagar Votação
                          </QItemSection>
                        </QItem>
                      </QList>
                    </QMenu>
                  </BtnIcon>
                </div>
              </QTd>
            </template>
          </QTable>
        </QTabPanel>
        <QTabPanel name="presence">
          <QTable
            :rows="presenceData"
            :columns="presenceColumns"
            :rows-per-page-options="[5, 10, 15, 20, 25]"
            row-key="id"
            flat
            bordered
            @row-click="showPresenceDetail = true"
          >
            <template #top>
              <div class="flex w-full justify-between items-center gap-3 mi2 mt-1 md:mt-0 -min-h-11">
                <h2 class="font-bold text-7 leading-6">
                  Credenciamento
                </h2>
              </div>
            </template>
            <template #body-cell-progress="{ value }">
              <QTd>
                <Progress
                  :percentage="value / (meeting?.countCreditors || 1) * 100"
                  :tooltip="`${value} de ${meeting?.countCreditors}`"
                />
              </QTd>
            </template>
            <template #body-cell-action="{ row }">
              <QTd>
                <div class="flex justify-end gap-2">
                  <BtnIcon
                    v-if="meeting.ableToRegisterPresence"
                    icon="i-carbon-stop-filled-alt"
                    color="error"
                    class="rounded-full"
                    tooltip="Encerrar Credenciamento"
                    :disabled="votings.some(voting => voting?.status === 'I')"
                    @click.stop="endPresence(row)"
                  />
                  <BtnIcon
                    v-else
                    icon="i-carbon-play-filled-alt"
                    class="rounded-full"
                    :tooltip="votings.some(voting => voting?.status === 'I') ? 'Tem uma Votação em Andamento!' :  (meeting.situation == 3) ? 'Iniciar Assembleia' : 'Iniciar Credenciamento'"
                    :disabled="votings.some(voting => voting?.status === 'I') || !meeting.id || (meeting.situation == 3 && meeting.status == 'I')"
                    @click.stop="startMeeting"
                  />
                </div>
              </QTd>
            </template>
            <template #body-cell-extra="{ row }">
              <QTd>
                <div class="flex justify-end">
                  <BtnIcon
                    flat
                    color="primary"
                    icon="i-carbon-overflow-menu-vertical"
                    class="rounded-full"
                    @click.stop
                  >
                    <QMenu>
                      <QList class="min-w-55">
                        <QItem
                          v-close-popup
                          clickable
                          @click="showPresenceDetail = true"
                        >
                          <QItemSection>
                            Detalhe do Credenciamento
                          </QItemSection>
                        </QItem>
                        <QItem
                          v-close-popup
                          clickable
                          @click="showPresenceGraph = true"
                        >
                          <QItemSection>
                            Exportar Gráficos
                          </QItemSection>
                        </QItem>
                      </QList>
                    </QMenu>
                  </BtnIcon>
                </div>
              </QTd>
            </template>
          </QTable>
        </QTabPanel>
      </QTabPanels>
    </div>

    <UpdateCreditor
      v-model:open="isEditing"
      :creditor="editingCreditor"
      :options="options"
      :representatives="representatives"
      @close="editingCreditor = {}"
      @update:creditor="loadCreditors"
    />

    <UpdateRepresentative
      v-model:open="isEditingRepresentative"
      :representative="editingRepresentative"
      @close="editingRepresentative = {}"
      @update:representative="loadRepresentatives"
    />

    <UploadCreditors
      v-model="showUploadCreditors"
      :object-id="attrs.id"
    />

    <NewRepresentative
      v-model:open="showNewRepresentative"
      :meeting-id="attrs.id"
    />

    <NewVoting
      v-model:open="showNewVoting"
      :meeting-id="attrs.id"
    />

    <DetailVoting
      v-model:open="showDetailVoting"
      :voting="selectedVoting"
    />

    <RunVoting
      v-model:open="showRunVoting"
      :voting="selectedVoting"
    />

    <RunPresence
      v-model:open="showRunPresence"
      :meeting-id="meeting.id"
    />

    <PresenceDetail
      v-model:open="showPresenceDetail"
      :meetingId="attrs.id"
      :socket="socket"
    />

    <PresenceGraphResult
      v-model:open="showPresenceGraph"
      :meeting="meeting"
    />

    <EditMeeting
      v-model="showEditMeeting"
      :meeting="meeting"
    />

    <VotingGraphResult
      v-model:open="graphResult.show"
      :voting="graphResult.selected"
      :meeting="meeting"
      @close="graphResult.selected = null"
    />

    <ExportReports
      v-model:open="showExportReports"
      :meeting="selectedVoting?.id ? {} : meeting"
      :voting="selectedVoting"
      @close="selectedVoting = {}"
    />

    <template #top>
      <div class="bg--base border-b-1 border--content/12">
        <div class="flex justify-between items-center gap-x-8 gap-y-2 px-4 py-2 max-w-400 mx-auto">
          <div class="flex min-w-0 flex-1 gap-x-8 gap-y-2 items-center">
            <BackButton />
            <div class="min-w-0 truncate">
              <Breadcrumbs :links="[{ label: 'Assembleias', url: '/assembleias' }, { label: meetingName }]" />
            </div>
          </div>
          <div class="ml-auto flex shrink-0 gap-3">
            <Btn
              label="Relatórios"
              outlined
              tooltip="Exportar Relatórios desta Assembleia"
              :disabled="!meeting.id"
              @click="showExportReports = true"
            />
            <Btn
              v-if="hasPermissions('can_manage_project')"
              label="Editar"
              outlined
              tooltip="Editar esta Assembleia"
              :disabled="!meeting.id"
              @click="showEditMeeting = true"
            />
            <Btn
              v-if="hasPermissions('can_manage_project')"
              label="Encerrar"
              outlined
              tooltip="Encerrar esta Assembleia"
              :disabled="!meeting.id"
              @click="endMeeting()"
            />

            <Btn
              label="Live"
              icon="i-carbon-video-filled"
              tooltip="Modo Apresentação"
              :disabled="!meeting.id"
              @click="router.push(`/assembleias/${attrs.id}/live`)"
            />
          </div>
        </div>
      </div>
    </template>
  </Page>
</template>

<route lang="yaml">
meta:
  authenticated: true
  notGuest: true
</route>
