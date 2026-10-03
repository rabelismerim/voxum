<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../services/api'
import { useQuasar } from 'quasar'

const router = useRouter()
const $q = useQuasar()

const form = ref({
  name: '',
  cpf_cnpj: '',
  creditor_class: 'QUIROGRAFARIO',
  credit_value: '',
})

const file = ref(null)
const loading = ref(false)

const handleCreateCreditor = async () => {
  loading.value = true
  try {
    await api.post('/creditors/', {
      ...form.value,
      credit_value: parseFloat(form.value.credit_value),
    })
    $q.notify({ type: 'positive', message: 'Credor cadastrado com sucesso!' })
    form.value = { name: '', cpf_cnpj: '', creditor_class: 'QUIROGRAFARIO', credit_value: '' }
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Erro ao cadastrar credor.' })
  } finally {
    loading.value = false;
  }
}

const handleFileUpload = async () => {
  if (!file.value) return
  loading.value = true

  const formData = new FormData()
  formData.append('file', file.value)

  try {
    await api.post('/import-creditors/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    $q.notify({ type: 'positive', message: 'Planilha importada com sucesso!' })
    file.value = null
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Erro ao importar arquivo.' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div className="min-h-screen bg-slate-50 p-6">
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <q-btn flat round icon="arrow_back" @click="router.push('/dashboard')" />
        <div className="font-bold text-xl text-slate-800">Gestão de Credores</div>
      </div>

      <!-- Form Manual -->
      <q-card flat bordered className="p-6 bg-white rounded-xl space-y-4">
        <div className="font-bold text-lg text-slate-800 border-b pb-2">Cadastrar Credor</div>
        <q-form @submit.prevent="handleCreateCreditor" className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <q-input v-model="form.name" label="Nome / Razão Social" outlined dense required />
          <q-input v-model="form.cpf_cnpj" label="CPF / CNPJ" outlined dense required />
          <q-select
            v-model="form.creditor_class"
            :options="[
              { label: 'Classe I - Trabalhista', value: 'TRABALHISTA' },
              { label: 'Classe II - Garantia Real', value: 'GARANTIA_REAL' },
              { label: 'Classe III - Quirografário', value: 'QUIROGRAFARIO' },
              { label: 'Classe IV - ME / EPP', value: 'ME_EPP' }
            ]"
            emit-value
            map-options
            label="Classe"
            outlined
            dense
          />
          <q-input v-model="form.credit_value" type="number" step="0.01" label="Valor do Crédito (R$)" outlined dense required />
          <q-btn type="submit" color="primary" label="Cadastrar Credor" className="md:col-span-2" unelevated :loading="loading" />
        </q-form>
      </q-card>

      <!-- Importação Lote -->
      <q-card flat bordered className="p-6 bg-white rounded-xl space-y-4">
        <div className="font-bold text-lg text-slate-800 border-b pb-2">Importação em Lote (.CSV / .XLSX)</div>
        <q-file v-model="file" label="Selecione o arquivo da planilha" outlined dense accept=".csv, .xlsx">
          <template v-slot:prepend>
            <q-icon name="attach_file" />
          </template>
        </q-file>
        <q-btn color="positive" label="Enviar Planilha" :disable="!file" unelevated :loading="loading" @click="handleFileUpload" />
      </q-card>
    </div>
  </div>
</template>