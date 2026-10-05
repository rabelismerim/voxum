<script setup>
const router = useRouter()
const attrs = useAttrs()
const { baseUrl } = useAmbient()
const { login, user } = useUser
const { socket, remove: removeSocket } = useSocket({ url: `V1/guest/meetings/${attrs.meetingId}` })

const isMeetingStarted = $computed(() => socket.value.channels?.meetingDetailGuest?.status === 'I')
const isMeetingStopped = $computed(() => socket.value.channels?.meetingDetailGuest?.status === 'E')

let loading = ref(true)
let meeting = ref({})
let votingStarted = ref(false)

async function loadMeeting() {
  try {
    meeting.value = await meetingService.getMeetingByGuest(attrs.meetingId)
  } catch (error) {
    print('ERROR ON LOADING MEETING AT VOTING HOME:', error)
  }
}

const checkVotingStart = () => {
  const now = new Date()
  const startDate = new Date(meeting.value.startDate)
  if (now >= startDate) {
    votingStarted.value = true
  }
}

onMounted(async () => {
  await login(`/guest/${attrs.meetingId}`)
  if (attrs.meetingId) await loadMeeting()
  checkVotingStart()
  loading.value = false
})
onBeforeUnmount(() => {
  removeSocket()
})
</script>

<template>
  <Page :loading="loading">
    <div class="md:flex md:items-center h-full px-4 max-w-400 min-w-60 mx-auto">
      <div
        class="flex flex-col-reverse pt-8 md:pt-0 pb-6 md:pb-0 md:grid md:grid-cols-2 md:gap-16 max-w-[min(1024px,100vw)] px-6 flex-1 mx-auto"
        :class="{'min-h-full': meeting.id}">
        <div class="flex flex-col justify-center gap-3 md:gap-4">
          <div class="flex flex-col items-start">
            <h1 class="font-extrabold text-3xl mt-3 md:text-4xl md:mt-8">
              Voxum - Votações
            </h1>
            <div class="text-gray text-lg md:text-xl">
              Sistema de Votação para Assembleias
            </div>
            <p v-if="!meeting.id" class="mt-4">
              Sistema para orquestração de votações em Assembleia Geral de Credores, para empresas em Recuperação Judicial.
            </p>
          </div>
          <div v-if="meeting.id" class="flex flex-col items-start">
            <div class="text-3 font-bold mt-1">Assembleia:</div>
            <div class="text-2xl font-bold">
              {{ meeting.name }}
            </div>
            <div class="flex gap-2 mt-1">
              <div class="bg--primary/10 py-.2 px-2 rounded-full border-1 border--primary/10">local: <span class="font-bold text--primary">{{ meeting.location.description }}</span></div>
              <div class="bg--primary/10 py-.2 px-2 rounded-full border-1 border--primary/10">Situação: <span class="font-bold text--primary">{{ meeting.statusDisplay }}</span></div>
            </div>
            <div class="text-3 font-bold mt-4">Descrição:</div>
            <div>
              {{ meeting.description }}
            </div>
            <div class="mt-4">
              <span class="font-bold text-4">Início:</span> <span class="bg--primary/10 py-.5 px-2 rounded-full border-1 border--primary/10">{{ formatDate(meeting.startDate, '@DD/@MM/@YYYY às @HH:@mm') }}</span>
            </div>
            <div v-if="isMeetingStopped" class="mt-4 flex flex-nowrap gap-2 bg--error/30 p-1 rounded-1 border-1 border--error/50 pr-2">
              <div class="i-carbon-information-filled text--error"/>
              <div>
                Esta Assembleia foi encerrada
              </div>
            </div>
            <div v-else-if="!isMeetingStarted && !isMeetingStopped" class="mt-4 flex flex-nowrap gap-2 bg--warning/30 p-1 rounded-1 border-1 border--warning/50 pr-2">
              <div class="i-carbon-information-filled text--warning"/>
              <div>
                Acompanhe a Assembleia pelo Zoom
              </div>
            </div>
            <Btn
              v-if="isMeetingStarted"
              label="Entrar"
              class="mt-5"
              @click="router.push(`/votacao/${attrs.meetingId}`)"
            />
          </div>
        </div>
        <div class="flex justify-center md:flex-col">
          <Img :src="`${baseUrl}/illustrations/splash.svg`" class="h-35vmin xs:h-full mb-5vmin md:m-0 md:min-h-10 md:h-70vmin md:min-w-0" />
        </div>
      </div>
    </div>
  </Page>
</template>

<route lang="yaml">
meta:
  layout: splash
</route>