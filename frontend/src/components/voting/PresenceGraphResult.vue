<script setup>
import { ref } from 'vue'
import domtoimage from 'dom-to-image-more'
import jsPDF from 'jspdf'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  meeting: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:open', 'close'])

const { baseUrl } = useAmbient()
const reportType = ref('count')

function onModalClose(value) {
  emit('update:open', value)
  if (!value) emit('close')
}

async function savePDF() {
  const { name, startDate } = props.meeting
  const element = document.querySelector('#presence_graph')

  if (!element) return

  domtoimage
    .toPng(element)
    .then(dataUrl => {
      const img = new Image()
      img.onload = () => {
        const width = img.naturalWidth
        const height = img.naturalHeight
        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)
        const imgData = canvas.toDataURL('image/png', 1.0)

        const doc = new jsPDF(width > height ? 'l' : 'p', 'pt', [width, height])
        doc.addImage(imgData, 'png', 0, 0, width, height)

        const fileName = `${normalizeText(`Voxum-${name ?? '_'}`).replaceAll(' ', '_')}_${(startDate ? dayjs(startDate) : dayjs()).format('DD-MM-YYYY')}.pdf`
        doc.save(fileName)
      }
      img.src = dataUrl
    })
    .catch(error => console.error('ERROR ON CREATING PNG TO EXPORT ON (PresenceGraphResult):', error))
}
</script>

<template>
  <Modal
    title="Gráfico de Resultado do Credenciamento"
    :model-value="open"
    modal-class="max-w-200"
    @update:model-value="onModalClose"
  >
    <div id="graph_results" class="p-4 overflow-y-auto max-h-80vh">
      <div class="flex gap-3 mb-4">
        <BtnToggle
          v-model="reportType"
          class="text-3!"
          :options="{
            count: 'Credores',
            amount: 'Créditos',
          }"
        />
      </div>

      <div>
        <div id="presence_graph" class="bg-white text-black! rounded-1">
          <div class="flex gap-4 w-full overflow-x-hidden mb-4">
            <div class="flex flex-1 gap-2 justify-between">
              <div>
                <div><span class="font-bold">Assembleia:</span> {{ meeting?.name }}</div>
                <div><span class="font-bold">Descrição:</span> {{ meeting?.description }}</div>
              </div>
            </div>
            <Img :src="`${baseUrl}/logo/voxum.svg`" class="w-50 -mr-10 ml-4" alt="logo of Voxum" />
          </div>
          <PresenceResult
            :meeting="meeting"
            :report-type="reportType"
            to-print
          />
        </div>
      </div>
    </div>

    <div class="p-3 flex justify-end bg--base border-t-1 border--content/12">
      <Btn label="Salvar" icon="i-carbon-document" @click="savePDF" />
    </div>
  </Modal>
</template>

<style>
#presence_graph {
  padding: 1rem;
  border: none !important;
}
#presence_graph * {
  border: none !important;
}
</style>