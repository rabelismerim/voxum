<script setup>
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
  data: {
    type: Object,
    default: () => ({}),
  },
  path: {
    type: String,
  },
  objectId: {
    type: String,
    // required: true,
  },
  name: {
    type: String,
    required: true,
  },
  hideActions: {
    type: Boolean,
  },
})
const emit = defineEmits(['cancel', 'fileSuccess', 'error'])
const {isMobile} = useAmbient()

let files = $ref([])
watchEffect(() => {
  files = props.modelValue.map(file => ({
    file,
    percentage: 0,
    uploading: false,
    done: false,
    controller: new AbortController(),
    error: null,
  }))
})
const uploadingFiles = $computed(() => files.filter(({ uploading }) => uploading))
const filesToRemove = $computed(() => files.filter(({ uploading }) => !uploading))

const removeFile = index => files.splice(index, 1)
function removeFiles() {
  files = files.filter(({ uploading }) => uploading)
}

function formatFileSize(size) {
  if (size > 10 ** 9)
    return `${(size / 10 ** 9).toFixed()} GB`
  if (size > 10 ** 6)
    return `${(size / 10 ** 6).toFixed()} MB`
  if (size > 10 ** 3)
    return `${(size / 10 ** 3).toFixed()} KB`
  return `${size} B`
}

function uploadFile(dataFile) {
  const regex = /(\[\d+\]|\.)/
  const formData = new FormData()

  Object.entries(flatten(props.data))
    .forEach(([key, value]) => {
      const snakeKey = key
        .split(regex)
        .map(item => item.match(regex) ? item : toSnake(item))
        .join('')
      formData.append(snakeKey, value)
    })

  formData.append('file', dataFile.file)
  formData.append('object_id', props.objectId)
  dataFile.uploading = true

  return apiFiles
    .post(`/v1/process_file/create/${props.path}/${props.name}/`, formData,
      {
        signal: dataFile.controller.signal,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress(progressEvent) {
          const percentage = Math.round((progressEvent.loaded * 99) / (progressEvent?.total || 1))
          dataFile.percentage = percentage
        },
      },
    )
}

const abortUpload = id => files[id].controller.abort()
function abortAll() {
  files.forEach(data => data.controller.abort())
  emit('cancel')
}

function uploadAll() {
  for (const data of files) {
    uploadFile(data)
      .then((result) => {
        emit('fileSuccess', result)
      })
      .catch((error) => {
        data.error = error.errors
        emit('error', error)
      })
      .finally(() => {
        data.done = true
        data.uploading = false
        data.percentage = 100
      })
  }
}

const canStartUpload = computed(() => files.length > 0)
const canCancelUpload = computed(() => files.length > 0 && uploadingFiles.length > 0)
const canRemoveFiles = computed(() => filesToRemove.length > 0)

defineExpose({
  uploadAll,
  canStartUpload,
  abortAll,
  canCancelUpload,
  removeFiles,
  canRemoveFiles,
})
</script>

<template>
  <div v-auto-animate class="pt-3">
    <div v-if="!hideActions" class="flex">
      <div class="flex gap-2">
        <Btn
          v-if="canStartUpload"
          label="Iniciar Upload"
          transparent
          @click="uploadAll"
        />
      </div>
      <div class="flex-1" />
      <div class="flex gap-2">
        <Btn
          v-if="canRemoveFiles"
          label="Limpar"
          transparent
          @click="removeFiles"
        />
        <Btn
          v-if="canCancelUpload"
          label="Cancelar Todos"
          transparent color="error"
          @click="abortAll"
        />
      </div>
    </div>
    <div
      v-for="({ file, percentage, done, error, uploading }, index) in files"
      :key="index"
      class="p-2 flex flex-col items-start sm:flex-row sm:items-center sm:gap-3"
    >
      <div class="flex gap-2 items-center">
        <div v-if="error" class="i-carbon-help-filled text-lg color--error cursor-help">
          <QTooltip v-if="!isMobile()">
            <div class="whitespace-pre">
              {{ error?.join('\n') }}
            </div>
          </QTooltip>
        </div>
        <div v-else class="i-carbon-document-attachment text-lg" />
        <div>
          <div class="font-bold">
            {{ file.name }}
          </div>
          <div class="text-xs">
            {{ formatFileSize(file.size * percentage / 99) }} de {{ formatFileSize(file.size) }}
          </div>
        </div>
      </div>
      <div class="flex gap-3 w-full flex-1 items-center">
        <div class="flex-1">
          <progress
            v-if="percentage > 0"
            :value="percentage"
            max="100"
            class="h-2 w-full"
            :style="{ '--color': !!error ? 'var(--error)' : 'var(--secondary)' }"
          />
          <div v-if="percentage > 0" class="text-xs flex justify-end">
            {{ !done ? `Subindo... ${percentage}%` : 'Finalizado' }}
          </div>
        </div>
        <div
          v-if="!done && percentage > 0"
          class="p-2 hover:bg--error/20 hover:color--error cursor-pointer tween"
          @click="abortUpload(index)"
        >
          <div class="i-carbon-close" />
        </div>
        <div
          v-if="!uploading"
          class="p-2 hover:bg--error/20 hover:color--error cursor-pointer tween rounded-1"
          @click="removeFile(index)"
        >
          <div class="i-carbon-trash-can" />
        </div>
      </div>
    </div>
  </div>
</template>

<style>
progress::-webkit-progress-bar {
  background: #0002;
}
progress::-webkit-progress-value {
  background: hsl(var(--color,0,0%,0%))
}
</style>
