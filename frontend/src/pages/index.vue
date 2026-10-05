<script setup>
const { baseUrl, localAuth } = useAmbient()
const router = useRouter()
const { user, login, loginLocal } = useUser
const username = ref('')
const password = ref('')
const isLoading = ref(false)
const loginError = ref('')
const hasLocalSession = computed(() => Boolean(sessionStorage.getItem('APP_TOKEN')))

const {prod: inProduction} = useAmbient()
const requested = ref(false)
const enter = () => router.push('/assembleias')

if (!localAuth || hasLocalSession.value)
  login().catch(() => {})

async function signIn() {
  loginError.value = ''
  isLoading.value = true

  try {
    await loginLocal(username.value, password.value)
    await router.push('/assembleias')
  }
  catch {
    loginError.value = 'Usuário ou senha inválidos. Verifique os dados e tente novamente.'
  }
  finally {
    isLoading.value = false
  }
}
</script>

<template>
  <Page>
    <div class="md:flex md:items-center px-4 w-full max-w-400 min-w-60 mx-auto">
      <div class="flex flex-col-reverse pt-8 md:pt-0 pb-6 md:pb-0 md:grid md:grid-cols-2 md:gap-16 max-w-[min(1200px,100vw)] px-6 flex-1 mx-auto">
        <div class="flex flex-col justify-center gap-3 md:gap-6 text-black">
          <h1 class="font-extrabold text-3xl mt-3 md:text-6xl md:mt-8">
            Voxum - Votações
          </h1>

          <div class="text-xl md:text-3xl">
            Sistema de Votação para Assembleias
          </div>

          <p>
            Sistema para orquestração de votações em Assembleia Geral de Credores,
            para empresas em Recuperação Judicial. Com o Voxum a área administra toda
            a cerimônia de credenciamento e votação de planos de pagamentos. Além
            disso, os usuários externos, os credores, registram a votação em tempo
            real.
          </p>
          <div class="flex flex-wrap gap-3">
            <form
              v-if="localAuth && !user.isActive"
              class="flex w-full max-w-100 flex-col gap-3"
              @submit.prevent="signIn"
            >
              <label class="flex flex-col gap-1">
                <span>Usuário</span>
                <input
                  v-model="username"
                  autocomplete="username"
                  class="rounded border border-gray-400 bg-white px-3 py-2 text-black"
                  required
                >
              </label>
              <label class="flex flex-col gap-1">
                <span>Senha</span>
                <input
                  v-model="password"
                  autocomplete="current-password"
                  class="rounded border border-gray-400 bg-white px-3 py-2 text-black"
                  required
                  type="password"
                >
              </label>
              <p v-if="loginError" class="text-red-700" role="alert">
                {{ loginError }}
              </p>
              <button
                class="rounded bg-primary px-4 py-2 font-semibold text-white disabled:opacity-60"
                :disabled="isLoading"
                type="submit"
              >
                {{ isLoading ? 'Entrando...' : 'Entrar' }}
              </button>
            </form>
            <div v-else-if="!user.isUserGuest">
              <Btn
                v-if="inProduction && user.authenticated && user.authorized && user.isActive && !isLoading"
                label="Entrar"
                @click="enter"
              />
              <Btn
                v-else-if="!inProduction && user.authorized && user.isActive && !isLoading"
                label="Entrar"
                @click="enter"
              />
              <Btn
                v-if="!isLoading && !user.isActive && inProduction"
                tag="a"
                :label="!requested ? 'Solicitar acesso' : 'Pedido de acesso solicitado'"
                :href="mailto"
                @click="requested = true"
              />
            </div>
          </div>
        </div>
        <div class="flex justify-center">
          <Img :src="`${baseUrl}/illustrations/splash.svg`" class="h-60 xs:h-full md:min-h-10 md:h-70vmin md:min-w-0" />
        </div>
      </div>
    </div>
  </Page>
</template>

<route lang="yaml">
meta:
  layout: splash
</route>