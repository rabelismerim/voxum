<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../services/api'
import { useQuasar } from 'quasar'

const router = useRouter()
const $q = useQuasar()

const username = ref('')
const password = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await api.post('/api/token/', {
      username: username.value,
      password: password.value,
    })
    localStorage.setItem('access_token', res.data.access)
    localStorage.setItem('refresh_token', res.data.refresh)
    router.push('/dashboard')
  } catch (err) {
    $q.notify({
      type: 'negative',
      message: 'Credenciais inválidas. Verifique usuário e senha.',
      icon: 'warning',
      position: 'bottom'
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-100 p-4">
    <q-card class="w-full max-w-md p-6 rounded-xl shadow-lg bg-white">
      <q-card-section class="text-center">
        <div class="text-2xl font-bold text-slate-800">Voxum - Autenticação</div>
      </q-card-section>

      <q-card-section>
        <q-form @submit.prevent="handleLogin" class="q-gutter-y-md">
          <q-input
            v-model="username"
            label="Usuário"
            outlined
            dense
            prepend-icon="person"
          />

          <q-input
            v-model="password"
            type="password"
            label="Senha"
            outlined
            dense
            prepend-icon="lock"
          />

          <div class="q-mt-lg">
            <q-btn
              type="submit"
              color="primary"
              class="full-width"
              unelevated
              :loading="loading"
              label="ENTRAR"
            />
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </div>
</template>