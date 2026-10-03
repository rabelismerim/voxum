<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../services/api'
import { connectMeetingSocket } from '../services/websocket'

const route = useRoute()
const router = useRouter()
const meetingId = route.params.id

const activeTab = ref('presence')
const meeting = ref(null)
const creditors = ref([])
const attendances = ref({})
const pollResults = ref(null)
let socket = null

onMounted(async () => {
  try {
    const [mRes, cRes, aRes] = await Promise.all([
      api.get(`/meetings/${meetingId}/`),
      api.get('/creditors/'),
      api.get(`/attendances/?meeting=${meetingId}`),
    ])

    meeting.value = mRes.data
    creditors.value = cRes.data.results || cRes.data

    const attMap = {}
    ;(aRes.data.results || aRes.data).forEach((a) => {
      attMap[a.creditor] = a.is_present
    })
    attendances.value = attMap
  } catch (err) {
    console.error(err)
  }

  socket = connectMeetingSocket(meetingId, (data) => {
    if (data.type === 'vote_update' || data.type === 'quorum_update') {
      pollResults.value = data.payload
    }
  })
})

onUnmounted(() => {
  if (socket) socket.close()
})

const toggleAttendance = async (creditorId) => {
  const isPresent = !attendances.value[creditorId]
  attendances.value[creditorId] = isPresent

  try {
    await api.post('/attendances/', {
      meeting: meetingId,
      creditor: creditorId,
      is_present: isPresent,
    })
  } catch (err) {
    console.error(err)
  }
}
</script>

<template>
  <div className="min-h-screen bg-slate-50 p-6 space-y-6">
    <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
      <div className="flex items-center gap-3">
        <q-btn flat round icon="arrow_back" @click="router.push('/dashboard')" />
        <div>
          <div className="font-bold text-xl text-slate-800">{{ meeting?.title }}</div>
          <div className="text-xs text-slate-500">Sala de Votação e Apuração</div>
        </div>
      </div>

      <q-tabs v-model="activeTab" dense active-color="primary" indicator-color="primary">
        <q-tab name="presence" label="Presença / Quórum" />
        <q-tab name="results" label="Apuração Final" />
      </q-tabs>
    </div>

    <!-- Tabela Presença -->
    <div v-if="activeTab === 'presence'" className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <q-markup-table flat borderless className="w-full">
        <thead>
          <tr className="text-left bg-slate-50 text-slate-600">
            <th className="p-3">Credor</th>
            <th className="p-3">CPF/CNPJ</th>
            <th className="p-3">Classe</th>
            <th className="p-3">Crédito</th>
            <th className="p-3 text-center">Presença</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in creditors" :key="c.id" className="border-b border-slate-100">
            <td className="p-3 font-medium">{{ c.name }}</td>
            <td className="p-3 text-slate-600">{{ c.cpf_cnpj }}</td>
            <td className="p-3 text-slate-600">{{ c.creditor_class }}</td>
            <td className="p-3 font-semibold">R$ {{ Number(c.credit_value).toLocaleString('pt-BR') }}</td>
            <td className="p-3 text-center">
              <q-btn
                :color="attendances[c.id] ? 'positive' : 'grey-5'"
                :label="attendances[c.id] ? 'Presente' : 'Ausente'"
                size="sm"
                unelevated
                @click="toggleAttendance(c.id)"
              />
            </td>
          </tr>
        </tbody>
      </q-markup-table>
    </div>

    <!-- Painel de Apuração -->
    <div v-if="activeTab === 'results'" className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
      <div className="font-bold text-lg text-slate-800">Quadro Geral de Apuração (Lei 11.101/2005)</div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <q-card v-for="cls in ['TRABALHISTA', 'GARANTIA_REAL', 'QUIROGRAFARIO', 'ME_EPP']" :key="cls" flat bordered className="p-4 bg-slate-50">
          <div className="font-bold text-xs text-primary border-b pb-2 uppercase">{{ cls }}</div>
          <div className="text-xs space-y-1 mt-2 text-slate-700">
            <div>Aprovações (Cabeças): <b>{{ pollResults?.[cls]?.yes?.heads || 0 }}</b></div>
            <div>Aprovações (Valor): <b>R$ {{ Number(pollResults?.[cls]?.yes?.value || 0).toLocaleString('pt-BR') }}</b></div>
            <div>Rejeições (Cabeças): <b>{{ pollResults?.[cls]?.no?.heads || 0 }}</b></div>
            <div>Rejeições (Valor): <b>R$ {{ Number(pollResults?.[cls]?.no?.value || 0).toLocaleString('pt-BR') }}</b></div>
          </div>
        </q-card>
      </div>
    </div>
  </div>
</template>