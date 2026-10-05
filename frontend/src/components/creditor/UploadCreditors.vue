<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
  },
  objectId: {
    type: String,
    required: true,
  },
})
const emit = defineEmits(['update:modelValue', 'update:uploadFiles', 'success', 'update:tab', 'update:filter'])

const { apiHost } = useAmbient()

let loading = $ref(false)
const form = ref(null)
const filesuploader = ref(null)

let selectedTab = $ref('carregamento')
const tabs = [
  { label: 'Carregamento', value: 'carregamento' },
  { label: 'Histórico', value: 'historico' },
]

function closeModal() {
  emit('update:modelValue', false)
}

let templateFiles = $ref([])

async function loadTemplateNames(path) {
  try {
    templateFiles = await filesService.getExampleNames(path)
  }
  catch (error) {
    print('ERROR ON LOADING FILE EXAMPLE:', error)
  }
}

let historicFiles = $ref([])
async function loadHistoricFiles() {
  loading = true
  try {
    const filesData = await filesService.getFiles(props.objectId)
    const files = await Promise.all(filesData.map(async (fileData) => {
      if (fileData && fileData.file) {
        const result = await filesService.getFileDetail(fileData.id)
        result.name = result.file.split('/').at(-1)
        return result
      }
      else {
        return null
      }
    }))
    historicFiles = files
      .filter(file => file !== null)
  }
  catch (error) {
    print('ERROR ON LOADING HISTORIC FILES:', error)
  }
  finally {
    loading = false
  }
}

const fileStatuses = [
  { label: 'Pendente', value: 'PENDING', color: '#eab308' },
  { label: 'Recebido', value: 'RECEIVED', color: '#0284c7' },
  { label: 'Iniciado', value: 'STARTED', color: '#0284c7' },
  { label: 'Processado', value: 'SUCCESS', color: '#22c55e' },
  { label: 'Falhou', value: 'FAILURE', color: '#ef4444' },
  { label: 'Revogado', value: 'REVOKED', color: '#9ca3af' },
  { label: 'Rejeitado', value: 'REJECTED', color: '#9ca3af' },
  { label: 'Reprocessando', value: 'RETRY', color: '#eab308' },
  { label: 'Ignorado', value: 'IGNORED', color: '#9ca3af' },
]

function getStatus(statusName) {
  const status = fileStatuses
    .find(status => status.value === statusName)
  return status
}

let uploadFiles = $ref([])
const updateFiles = newFiles => uploadFiles = newFiles
const log = value => value === 'historico' && loadHistoricFiles()

function onClose() {
  uploadFiles = []
  selectedTab = 'carregamento'
}

onMounted(() => {
  loadTemplateNames('meeting_creditors')
})
</script>

<template>
  <Modal
    :loading="loading"
    :model-value="modelValue"
    title="Carregamento em massa de credores"
    modal-class="max-w-200"
    @update:model-value="(value) => emit('update:modelValue', value)"
    @close="onClose"
  >
    <div>
      <TabFilter
        v-model="selectedTab"
        :items="tabs"
        class="mb-0!"
        @update:model-value="log"
      />
      <QTabPanels
        v-model="selectedTab"
      >
        <QTabPanel
          name="carregamento"
          class="px-4 bg--background/40 max-h-[calc(100vh-14rem)]"
        >
          <div class="mb-3 pt-3">
            <div class="font-bold mb-4 text-lg">
              Download do template
            </div>
            <div>
              <a
                v-for="(name, index) in templateFiles"
                :key="name"
                :href="`${apiHost}/voxum/api/v1/process_file/examples/detail/${name}/`"
                target="_blank"
                class="p-2 border--content/12 bg--base font-bold text--primary flex justify-between cursor-pointer hover:text--secondary hover:bg--secondary/10 tween rounded-1"
                :class="{
                  'border-1': index === 0,
                  'border-x-1 border-b-1': index > 0,
                }"
              >
                <div class="flex gap-2 items-center">
                  <div class="i-carbon-xls" />
                  {{ name }}
                </div>
                <div class="flex gap-1 items-center">
                  Baixar
                  <div
                    class="i-carbon-document-download"
                  />
                </div>
              </a>
            </div>
          </div>

          <div class="text-h9" style="font-weight: bold">
            <DropZone
              :types="['xls', 'xlsx']"
              @drop="updateFiles"
            />
            <FilesUploader
              ref="filesuploader"
              v-model="uploadFiles"
              path="meeting_creditors"
              :object-id="objectId"
              name="massive_create_creditors"
              hide-actions
            />
          </div>
        </QTabPanel>

        <QTabPanel
          name="historico"
          class="px-4 bg--background/40 overflow-y-auto max-h-[calc(100vh-14rem)]"
        >
          <div class="pb-3">
            <div class="flex gap-3 font-bold py-4 text-lg">
              Histórico de arquivos carregados no sistema ({{ historicFiles?.length }})
              <ReloadBtn @click="loadHistoricFiles" />
            </div>
            <div>
              <div>
                <Expandable
                  v-for="(file) in historicFiles"
                  :key="file.id"
                  class="border-1 border--content/12 bg--base font-bold justify-between mb-2 rounded-1"
                  show-divider
                  title-class="px-2! py-1!"
                >
                  <template #title>
                    <div class="flex items-center gap-2 justify-between flex-1">
                      <div class="flex gap-2 items-center">
                        <div class="i-carbon-xls" />
                        <div>{{ file.name }}</div>
                        <div v-if="file.updatedAt">
                          - {{ formatDate(file.updatedAt, '@DD/@MM/@YYYY às @HH:@mm:@ss') }}
                        </div>
                      </div>
                      <StatusTag
                        :label="getStatus(file.task?.status)?.label"
                        :color="getStatus(file.task?.status)?.color"
                      />
                    </div>
                  </template>
                  <div
                    v-if="(file?.errors?.length > 0)"
                  >
                    <div
                      v-for="({ error, statusDisplay }, index) in file.errors"
                      :key="index"
                      class="flex justify-between"
                      :class="{
                        'border-t-1 border--content/12': index > 0,
                      }"
                    >
                      <div class="flex gap-2 items-center">
                        <div class="flex gap-2 items-center font-bold text-red-500">
                          Erro {{ index + 1 }}:
                        </div>
                        <div>
                          {{ error }} - {{ statusDisplay }}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else-if="file.task?.status === 'STARTED'" class="flex justify-center">
                    Iniciou o processamento da fila.
                  </div>
                  <div v-else-if="file.task?.status === 'PENDING'" class="flex justify-center">
                    O arquivo está aguardando na fila de processamento.
                  </div>
                  <div v-else-if="file.task?.status === 'SUCCESS'" class="flex justify-center">
                    O arquivo foi processado com sucesso.
                  </div>
                  <div v-else class="flex justify-center">
                    Houve um problema ao processar o arquivo.
                  </div>
                </Expandable>
              </div>
            </div>
          </div>
        </QTabPanel>
      </QTabPanels>
      <div class="p-3 flex justify-end border-t-1 border--content/12">
        <div v-if="selectedTab === 'carregamento'" class="flex flex-1">
          <div class="flex gap-2">
            <Btn
              v-if="filesuploader?.canCancelUpload"
              label="Cancelar Todos"
              outlined color="error"
              @click="filesuploader?.abortAll()"
            />
            <Btn
              v-else
              :disabled="!filesuploader?.canRemoveFiles"
              label="Limpar"
              outlined color="error"
              @click="filesuploader?.removeFiles()"
            />
          </div>
          <div class="flex-1" />
          <div class="flex gap-2">
            <Btn
              :disabled="!filesuploader?.canStartUpload"
              label="Iniciar Upload"
              @click="filesuploader?.uploadAll()"
            />
          </div>
        </div>
        <Btn
          v-if="selectedTab === 'historico'"
          label="Fechar"
          color="primary"
          @click="closeModal"
        />
      </div>
    </div>
  </Modal>
</template>