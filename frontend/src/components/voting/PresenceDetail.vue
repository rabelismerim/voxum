<script setup>
import { ref, computed, watchEffect } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  meetingId: {
    type: String,
    default: '',
  },
  socket: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['update:open', 'close'])

const { isMobile } = useAmbient()
const { dialog } = useQuasar()

const modal = ref(null)
const loading = ref(false)
const filterBy = ref('')

const {
  pagination: creditorsPagination,
  updatePagination: updateCreditorsPagination,
  items: creditors,
  get: loadCreditors,
  loading: loadingCreditors,
} = meetingService.getCreditors(props.meetingId, props.socket)

updateCreditorsPagination?.({ filterColumn: 'first_name' })

watchEffect(() => {
  if (props.open) loadCreditors()
})

function setPresence(creditor) {
  dialog({
    title: 'Registrando presença de credor',
    message: 'Você tem certeza que esta pessoa está ciente desta ação?',
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    loading.value = true
    try {
      const result = await presenceService.registerVoterPresence(creditor)
      if (result?.id) {
        notify?.({ message: 'O credor foi registrada com sucesso!' })
      }
    }
    catch (error) {
      console.error('ERROR ON REGISTRING CREDITOR PRESENCE ON PRESENCE DETAIL:', error)
    }
    finally {
      loading.value = false
    }
  })
}

function onModalClose(value) {
  emit('update:open', value)
  if (!value) emit('close')
}

const isLoading = computed(() => loadingCreditors.value)

const creditorVotesColumns = [
  {
    name: 'first_name',
    field: 'guest',
    label: 'Credor',
    align: 'left',
    sortable: true,
    format: value => value?.user ? `${value?.user?.firstName} ${value?.user?.lastName}` : '-',
  },
  {
    name: 'legal_number',
    field: 'guest',
    label: 'Documento',
    align: 'left',
    sortable: true,
    format: value => formatLegalNumber(value?.entity?.legalNumber) ?? '-',
  },
  {
    name: 'email',
    field: 'guest',
    label: 'E-mail',
    align: 'left',
    format: value => value?.user?.email ?? '-',
  },
  {
    name: 'credit',
    field: 'creditValue',
    label: 'Valor',
    align: 'left',
    format: value => formatMoney(value),
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
    name: 'is_accredited',
    field: 'presence',
    label: 'Credenciamento',
    align: 'left',
    sortable: true,
    format: value => value?.isAccredited ? '✔️' : '-',
  },
  {
    name: 'edit',
    field: 'result',
    label: 'Editar',
    align: 'left',
  },
]
</script>

<template>
  <Modal
    ref="modal"
    title="Detalhes do Credenciamento"
    :model-value="open"
    modal-class="max-w-260"
    can-fullscreen
    @update:model-value="onModalClose"
  >
    <template #side>
      <div class="flex flex-1 justify-between items-center mr-15">
        <ReloadBtn
          tooltip="Recarregar Lista"
          @click="loadCreditors()"
        />
        <SearchFilter
          v-model:search="creditorsPagination.filterBy"
          v-model:field="creditorsPagination.filterColumn"
          auto-size
          class="my-1.5"
          :options="{
            first_name: 'Nome do Credor',
            legal_number: 'CPF/CNPJ',
          }"
        />
      </div>
    </template>

    <QTable
      v-model:pagination="creditorsPagination"
      :rows="creditors"
      :columns="creditorVotesColumns"
      :filter="filterBy"
      :no-data-label="isLoading ? 'carregando...' : 'Nenhum credor listado'"
      :rows-per-page-options="[5, 10, 15, 20, 25]"
      :loading="isLoading"
      row-key="id"
      flat
      bordered
      color="secondary"
      class="detail-voting-table"
      :class="{
        'max-h-[calc(100vh-5.4rem)]': modal?.isFullscreen,
        'max-h-[calc(100vh-15rem)]': !modal?.isFullscreen,
      }"
      table-header-class="sticky top-0 z-1 backdrop-blur"
      @request="updateCreditorsPagination($event?.pagination)"
    >
      <template #body-cell-progress="{ value }">
        <QTd>
          <Progress :percentage="value" />
        </QTd>
      </template>

      <template #body-cell-status="{ value }">
        <QTd>
          <div class="flex justify-end">
            <StatusTag :label="votingStatus[value]" :color="votingStatusColors[value]" />
          </div>
        </QTd>
      </template>

      <template #body-cell-votingcount="{ value, row }">
        <QTd>
          <div class="max-w-60 text-ellipsis overflow-hidden">
            {{ value }}
          </div>
          <QTooltip v-if="row.votingcount?.length && !isMobile()">
            <ul class="list-disc">
              <li v-for="item in row.votingcount" :key="item.id">
                • {{ item.votingcount?.guest?.user?.firstName || '-' }}
                {{ item.votingcount?.guest?.user?.lastName || '-' }}
                {{ item.votingcount?.guest?.user?.email || '-' }}
              </li>
            </ul>
          </QTooltip>
        </QTd>
      </template>

      <template #body-cell-edit="{ row }">
        <QTd class="flex justify-center">
          <BtnIcon
            icon="i-carbon-request-quote"
            color="primary"
            @click="setPresence(row)"
          />
        </QTd>
      </template>
    </QTable>
  </Modal>
</template>

<style>
.detail-voting-table .q-table__progress {
  position: sticky;
  top: 3rem;
  z-index: 1;
}
</style>