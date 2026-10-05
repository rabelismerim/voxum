<script setup>
import { ref, computed } from 'vue'
import domtoimage from 'dom-to-image-more'
import jsPDF from 'jspdf'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  voting: {
    type: Object,
    default: () => ({}),
  },
  meeting: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:open', 'close'])

const { baseUrl } = useAmbient()

function onModalClose(value) {
  emit('update:open', value)
  if (!value) emit('close')
}

const reportType = ref('count')
const withAbstention = ref('false')
const showDetail = ref(false)

const choices = computed(() => props.voting?.results ?? [])

async function savePDF() {
  const { name, startDate } = props.meeting
  const element = document.querySelector('#voting_graph')

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
        doc.save(
          `${normalizeText(`Voxum-${name ?? '_'}`).replaceAll(' ', '_')}_${(startDate ? dayjs(startDate) : dayjs()).format('DD-MM-YYYY')}.pdf`
        )
      }
      img.src = dataUrl
    })
    .catch(error => console.error('ERROR ON CREATING PNG TO EXPORT ON (VotingGraphResult):', error))
}
</script>

<template>
  <Modal
    title="Gráfico de Resultado da Votação"
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
            deliberation: 'Deliberação',
            prj: 'PRJ',
          }"
        />
        <BtnToggle
          v-model="withAbstention"
          class="text-3!"
          :options="{
            false: 'Abstenção Total',
            true: 'Abstenção Parcial',
          }"
        />
        <QToggle v-if="['deliberation', 'prj'].includes(reportType)" v-model="showDetail" label="Exibir Detalhes" />
      </div>

      <div style="zoom: 0.5">
        <div id="voting_graph" class="bg-white text-black! rounded-1">
          <div class="flex gap-4 w-full">
            <div class="flex flex-1 gap-2 justify-between">
              <div>
                <div><span class="font-bold">Assembleia:</span> {{ meeting?.name }}</div>
                <div><span class="font-bold">Descrição:</span> {{ meeting?.description }}</div>
              </div>
              <div class="flex items-center">
                <span class="font-bold">Horário:</span> {{ formatDate(voting?.startDate, '@DD/@MM/@YYYY às @HH:@mm') }}
              </div>
            </div>
            <Img :src="`${baseUrl}/logo/voxum.svg`" class="w-50 -mr-10 ml-4" alt="logo of Voxum" />
          </div>

          <div class="font-bold text-6 mb-4">{{ voting?.description }}</div>

          <CreditorsResult
            v-if="reportType === 'count'"
            :results="choices"
            :with-abstention="withAbstention === 'true'"
            :width="1000"
            to-print
          />
          <AmountResult
            v-else-if="reportType === 'amount'"
            :results="choices"
            :with-abstention="withAbstention === 'true'"
            :width="1000"
            to-print
          />
          <DeliberationResult
            v-if="reportType === 'deliberation'"
            :with-abstention="withAbstention === 'true'"
            :results="choices"
            to-print
            :show-detail="showDetail"
          />
          <PrjResult
            v-else-if="reportType === 'prj'"
            :results="choices"
            :with-abstention="withAbstention === 'true'"
            :width="1000"
            to-print
            :show-detail="showDetail"
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
#voting_graph {
  padding: 1rem;
  border: none !important;
}
#voting_graph * {
  border: none !important;
}
</style>