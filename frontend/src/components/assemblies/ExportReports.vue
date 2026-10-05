<script setup>
const props = defineProps({
  open: {
    type: Boolean,
  },
  meeting: {
    type: Object,
    default: () => ({}),
  },
  voting: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:open', 'close'])

const { socket } = useSocket({ url: 'V1/general' })

const localId = $computed(() => props.voting?.id ?? props.meeting?.id)
const localReports = $computed(() => socket.value.channels?.[props.voting?.id ? 'reportVotingList' : 'reportMeetingList']?.data
  ?.reduce((acc, curr) => {
    const { meetingId, votingId } = curr
    const usePath = props.voting?.id ? votingId : meetingId
    if (!acc[usePath]) acc[usePath] = []
    acc[usePath].push(curr)
    return acc
  }, {}) ?? {})

let loading = $ref(false)

let reportOptions = $ref([])
async function loadReportOptions() {
  loading = true
  try {
    const {voting, meeting} = await reportsService.getOptions()
    reportOptions = props.voting.id ? voting : meeting
  }
  catch (error) {
    print('ERROR ON LOAD REPORTS OPTIONS:', error)
  }
  finally {
    loading = false
  }
}

const reports = $computed(() => reportOptions
  .map(({ legend, id }) => ({
    typeDisplay: legend,
    reportType: id,
    ...localReports[localId]
      ?.find(({ typeDisplay }) => typeDisplay === legend),
  })))

watch(() => props.open, open => {
  if(!open) return
  if (localId) loadReportOptions()
})

async function generateReport(report) {
  try {
    const endpoint = props.voting?.id ? 'generateVotingReport' : 'generateMeetingReport'
    await reportsService[endpoint](localId, report.reportType)
  }
  catch (error) {
    print('ERROR ON GENERATE REPORT:', error)
  }
}

function getStatus(report) {
  const status = report?.task?.status
  if(status === 'FAILURE') return {label: 'Erro', color: '#d9291c'}
  if(status === 'SUCCESS') return {label: 'Gerado', color: '#87bb25'}
  if(status === 'RETRY') return {label: 'Tentando Novamente', color: '#007db3'}
  return {label: 'Processando...', color: '#007db3'}
}
</script>

<template>
  <Modal
    :model-value="open"
    :loading="loading"
    :title="`Exportar Relatórios ${props.voting?.id ? 'da Votação' : 'da Assembléia'}`"
    modal-class="max-w-200"
    @update:model-value="value => emit('update:open', value)"
    @close="emit('close')"
  >
    <template #side>
      <ReloadBtn
        :loading="loading"
        tooltip="Recarregar Lista"
        @click="loadReportOptions"
      />
    </template>
    <div class="px-4 py-2 overflow-y-auto max-h-[calc(100vh_-_200px)]">
      <div v-if="reports.length">
        <div
          v-for="report in reports"
          :key="report.reportType"
          class="pl-4 p-2 pr-2 border-1 border--content/12 rounded-1 flex items-center justify-between gap-3 mb-2"
        >
          <div>
            <div class="font-bold">
              {{ report.typeDisplay ?? '...' }}
            </div>
            <div class="text-xs">
              Gerado em: {{ formatDate(report.updatedAt, '@DD/@MM/@YYYY às @HH:@mm', 'Não gerado...') }}
            </div>
          </div>
          <div class="flex gap-2 items-center">
            <StatusTag
              v-if="report.task"
              :label="getStatus(report).label"
              :color="getStatus(report).color"
            />
            <Btn
              label="Gerar Novo"
              :loading="report?.task?.status === 'PENDING'"
              :disabled="report?.task?.status === 'PENDING'"
              loading-label="Processando..."
              outlined
              @click="generateReport(report)"
            />
            <Btn
              v-if="report.file"
              tag="a"
              label="Download"
              icon="i-carbon-download"
              target="_blank"
              :href="report.file"
            />
          </div>
        </div>
      </div>
      <div v-else class="p-2 text-center">
        Nenhum relatório no momento...
      </div>
    </div>
  </Modal>
</template>
