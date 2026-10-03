<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../services/api'
import { useRouter } from 'vue-router'

const router = useRouter()

const loading = ref(true)
const companies = ref([])
const meetings = ref([])

const fetchDashboardData = async () => {
  loading.value = true
  try {
    // Faz a chamada dos dados incluindo o prefixo /api/
    const [creditorsRes, meetingsRes] = await Promise.all([
      api.get('/api/creditors/'),
      api.get('/api/meetings/')
    ])
    
    companies.value = creditorsRes.data
    meetings.value = meetingsRes.data
  } catch (error) {
    console.error('Erro ao carregar os dados do dashboard:', error)
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  router.push('/login')
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<template>
  <q-layout view="lHh Lpr lFf" class="bg-slate-50">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title class="font-bold">
          Voxum - Painel Principal
        </q-toolbar-title>
        <q-btn flat round icon="logout" @click="handleLogout" title="Sair" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md max-w-7xl class-auto">
        <div v-if="loading" class="flex justify-center items-center py-20">
          <q-spinner-dots color="primary" size="40px" />
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Card de Assembleias / Reuniões -->
          <q-card class="shadow-sm border border-slate-200 rounded-lg">
            <q-card-section class="bg-white border-b border-slate-100">
              <div class="text-lg font-semibold text-slate-800">Assembleias Recentes</div>
            </q-card-section>
            
            <q-card-section>
              <q-list v-if="meetings.length > 0" separator>
                <q-item v-for="meeting in meetings" :key="meeting.id" clickable v-ripple>
                  <q-item-section>
                    <q-item-label class="font-medium">{{ meeting.title || meeting.name }}</q-item-label>
                    <q-item-label caption>Data: {{ meeting.date || 'A definir' }}</q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-badge color="blue-6">{{ meeting.status || 'Agendada' }}</q-badge>
                  </q-item-section>
                </q-item>
              </q-list>
              <div v-else class="text-slate-500 text-center py-4">
                Nenhuma assembleia cadastrada.
              </div>
            </q-card-section>
          </q-card>

          <!-- Card de Credores / Empresas -->
          <q-card class="shadow-sm border border-slate-200 rounded-lg">
            <q-card-section class="bg-white border-b border-slate-100">
              <div class="text-lg font-semibold text-slate-800">Credores / Empresas</div>
            </q-card-section>

            <q-card-section>
              <q-list v-if="companies.length > 0" separator>
                <q-item v-for="item in companies" :key="item.id">
                  <q-item-section>
                    <q-item-label class="font-medium">{{ item.name || item.corporate_name }}</q-item-label>
                    <q-item-label caption>Doc: {{ item.document || item.cpf_cnpj }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
              <div v-else class="text-slate-500 text-center py-4">
                Nenhum credor cadastrado.
              </div>
            </q-card-section>
          </q-card>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>