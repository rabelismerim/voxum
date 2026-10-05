<script setup>
const attrs = useAttrs()
const { routerBaseUrl } = useAmbient()

const { dialog } = useQuasar()
const { login } = useUser

let loading = $ref(false)
const showData = $ref(false)
const now = useNow()

const { toggle, accordion } = useAccordion(false, false)

const { socket, open } = useSocket({ url: `V1/meetings/${attrs.id}` }, { update: true })
const meeting = $computed(() => socket.value.channels.meetingDetail ?? {})
const meetingName = $computed(() => meeting?.name)
const voting = $computed(() => socket.value.channels.votingProgress ?? {})
const totalVotingCreditors = $computed(() => voting?.qualifiedCreditors ?? 0)
const creditsAmount = $computed(() => formatMoney(meeting?.totalCredit ?? 0))
const onVoting = $computed(() => voting?.startDate && voting?.endDate && now?.value > new Date(voting?.startDate) && now?.value < new Date(voting?.endDate))
const classesNames = $computed(() => ([
  ...new Set((voting.classChoice ?? [])
    .map(({ classe: name }) => name)
    .sort())
]))

const backendNotification = $computed(() => socket.value.channels?.notificationToast ?? {})
watch(() => backendNotification, notification => {
  if (notification?.data?.message) notify(notification.data)
})

let showTop = $ref(true)
watch(() => voting, () => {
  if (voting?.id) showTop = false
  if (!voting?.id) showTop = true
})

const reportType = $ref('count')
const withAbstention = $ref('false')
const choices = $computed(() => voting?.results ?? [])

const url = $computed(() => `${window.location.host}/${routerBaseUrl}/guest/${attrs.id}`)
const copyUrl = () => {
  copyToClipboard(url)
  notify({ message: 'Link copiado para a área de transferência!' })
}

const showRunPresence = $ref(false)
const onPresence = $computed(() => meeting?.ableToRegisterPresence && !voting?.id)
const presenceResultCount = $computed(() => {
  const { present, total } = meeting?.creditorsPresenceStatus?.reduce((acc, { countAccredited, countCreditors }) => {
    acc.total = acc.total + countCreditors
    acc.present = acc.present + countAccredited
    return acc
  }, { present: 0, total: 0 })
  return { present, total, percentage: present / total * 100 }
})
const presenceResultAmount = $computed(() => {
  const { present, total } = meeting?.creditorsCredit?.reduce((acc, { totalCreditAccredited, totalCredit }) => {
    acc.total = acc.total + totalCredit
    acc.present = acc.present + totalCreditAccredited
    return acc
  }, { present: 0, total: 0 })
  return { present, total, percentage: present / total * 100 }
})

async function endPresence() {
  dialog({
    title: 'Encerrando Credenciamento',
    message: `Você confirma o fim do período de Credenciamento?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    loading = true
    try {
      await presenceService.finish(meeting.id)
      notify({ message: 'Credenciamento encerrado com sucesso!' })
    }
    catch (error) {
      print('ERROR ON ENDING PRESENCE ON LIVE:', error)
    }
    finally {
      loading = false
    }
  })
}

const showDetail = $ref(false)
const votingList = ref(null)

const presenceContainer = ref(null)
const { width: presenceWidth } = useElementSize(presenceContainer)
const votingContainer = ref(null)
const { width: votingWidth } = useElementSize(votingContainer)

const notNaN = num =>
  Number.isNaN(num) ? 0 : num

onMounted(() => {
  login()
})
</script>

<template>
  <Page :loading="loading">
    <div class="w-full flex flex-col flex-nowrap min-h-full max-w-400 min-w-85 mx-auto px-8 py-8 pb-20">
      <div class="flex gap-2 mb-2 text-3">
        <div
          v-for="(name, i) in classesNames"
          :key="i"
          class="py-.6 px-2 font-bold bg-gray/20 rounded-full"
        >
          {{ name }}
        </div>
      </div>
      <div class="flex mb-4 items-center">
        <div class="flex-1">
          <h2 class="font-bold text-4xl mb-2">
            {{ voting.description }}
          </h2>
          <div v-if="meeting?.id" class="color--secondary font-bold text-xl">
            Créditos: {{ creditsAmount }}
          </div>
        </div>
        <div v-if="onPresence" class="flex items-end justify-center gap-3 flex-nowrap">
          <button
            class="group h-9 aspect-square text-lg border-1 border--primary hover:bg--primary/20 rounded-1 flex justify-center items-center"
            @click="showData = !showData"
          >
            <div
              class="color--primary"
              :class="[showData ? 'i-carbon-view' : 'i-carbon-view-off']"
            />
          </button>
          <Btn label="Prorrogar" outlined @click="showRunPresence = true" />
          <Btn label="Encerrar" @click="endPresence" />
        </div>
        <div v-else-if="onVoting" class="flex items-end justify-center gap-3 flex-nowrap">
          <button
            class="group h-9 aspect-square text-lg border-1 border--primary hover:bg--primary/20 rounded-1 flex justify-center items-center"
            @click="showData = !showData"
          >
            <div
              class="color--primary"
              :class="[showData ? 'i-carbon-view' : 'i-carbon-view-off']"
            />
          </button>
          <Btn label="Prorrogar" outlined @click="votingList.runVoting('extend', voting)" />
          <Btn label="Encerrar" @click="votingList.endVoting()" />
        </div>
      </div>

      <div
        ref="presenceContainer"
        v-if="onPresence"
        class="flex-1 flex flex-col"
      >
        <div class="flex-1" />
        <div class="flex flex-nowrap font-bold text--primary text-6 uppercase mb-3 gap-2">
          <div class="bg--primary text--base text-4 h-8 min-w-8 w-8 rounded-full flex justify-center items-center">
            <div class="i-carbon-user-identification"></div>
          </div>
          Credenciamento em Andamento
        </div>
        <div
          v-if="showData"
          class="border-1 border--content/12 bg--base p-6 rounded"
        >
          <div class="flex mb-6">
            <BtnToggle
              v-model="reportType"
              :options="{
                count: 'Credores',
                amount: 'Créditos',
              }"
            />
          </div>
          <PresenceResult
            :reportType="reportType"
            :meeting="meeting"
            :width="presenceWidth"
          />
        </div>
        <div v-else>
          <div class="text-2xl font-bold mb-3">
            {{ presenceResultCount?.present }} de {{ presenceResultCount?.total }}
          </div>
          <Progress
            label="Credenciados"
            :percentage="notNaN(presenceResultCount.percentage)"
          />
        </div>
        <div class="flex-1" />
      </div>

      <div v-else-if="onVoting" class="flex-1 flex flex-col">
        <div class="flex-1" />
        <div class="flex flex-nowrap font-bold text--primary text-6 uppercase mb-3 gap-2">
          <div class="bg--primary text--base text-4 h-8 min-w-8 w-8 rounded-full flex justify-center items-center">
            <div class="i-carbon-report"></div>
          </div>
          Votação em Andamento
        </div>
        <div
          ref="votingContainer"
          v-if="showData"
          class="border-1 border--content/12 bg--base p-6 rounded-1"
        >
          <div class="flex mb-4 gap-3">
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
          <CreditorsResult
            v-if="reportType === 'count'"
            :results="choices"
            :with-abstention="withAbstention === 'true'"
            :width="votingWidth"
          />
          <AmountResult
            v-else-if="reportType === 'amount'"
            :results="choices"
            :with-abstention="withAbstention === 'true'"
            :width="votingWidth"
          />
          <DeliberationResult
            v-if="reportType === 'deliberation'"
            :with-abstention="withAbstention === 'true'"
            :results="choices"
            :show-detail="showDetail"
          />
          <PrjResult
            v-else-if="reportType === 'prj'"
            :results="choices"
            :with-abstention="withAbstention === 'true'"
            :width="votingWidth"
            :show-detail="showDetail"
          />
        </div>
        <div v-else class="w-full border-1 border--content/12 p-6 bg--base rounded">
          <VotingResult :voting="voting" />
        </div>
        <div class="flex-1" />
      </div>

      <div v-else class="flex-1 flex justify-center items-center text-center font-bold text-7vmin pb-10vmin color-gray">
        Aguardando Início da Votação
      </div>
      <End />
    </div>

    <RunPresence
      v-model:open="showRunPresence"
      :meeting-id="meeting?.id"
      type="extend"
    />

    <template #top>
      <div class="bg--base border-b-1 border--content/12">
        <div class="flex justify-between items-center gap-8 px-4 py-2 max-w-400 mx-auto">
          <div class="flex gap-8">
            <BackButton />
            <Breadcrumbs
              :links="[{ label: 'Assembleias', url: '/assembleias' }, { label: meetingName, url: `/assembleias/${attrs.id}` }, { label: 'Live' }]"
              class="hidden md:flex!"
            />
          </div>
          <SocketTag
            :socket="socket"
            @click="open"
          />
        </div>
        <Expandable
          hide-title
          v-model:open="showTop"
        >
          <div class="md:px-8 max-w-400 mx-auto">
            <div class="flex justify-between gap-x-5 gap-y-2">
              <div>
                <h1 class="font-bold text-2xl mb-4">
                  Assembleia {{ meetingName }}
                </h1>
                <div class="flex gap-5">
                  <div>
                    <div class="font-bold text-gray">
                      VOTOS
                    </div>
                    <div>{{ voting.results?.reduce((acc, { countVoters }) => countVoters + acc, 0) ?? 0 }}/{{ totalVotingCreditors }}</div>
                  </div>
                  <div class="border-l-1 border--content/12" />
                  <div>
                    <div class="font-bold text-gray">
                      LOCAL
                    </div>
                    <div>{{ meeting?.location?.description ?? '-' }}</div>
                  </div>
                  <div class="border-l-1 border--content/12" />
                  <div>
                    <div class="font-bold text-gray">
                      SITUAÇÃO
                    </div>
                    <div>{{ meeting?.situationDisplay ?? '-' }}</div>
                  </div>
                  <div class="border-l-1 border--content/12" />
                  <div>
                    <div class="font-bold text-gray">
                      DESCRIÇÃO
                    </div>
                    <div>{{ meeting?.description ?? '-' }}</div>
                  </div>
                </div>
              </div>
              <div class="border-1 border--content/12 bg-gray/20 p-2 flex gap-4 rounded-1">
                <div class="flex">
                  <div>
                    <div class="font-bold text-gray text-3">
                      <button
                        class="border-1 border--content/12 p-1 rounded-1 bg--base/50 hover:bg--secondary hover:text-white"
                        @click="copyUrl"
                      >
                        <div class="i-carbon-copy" />
                      </button>
                      ACESSE PARA VOTAR
                    </div>
                    <div class="max-w-38 break-all text-3">{{ url }}</div>
                  </div>
                </div>
                <QR :content="url" />
              </div>
            </div>
          </div>
          <template #append>
            <BtnIcon
              icon="i-carbon-chevron-down"
              rounded
              outlined
              :tooltip="showTop ? 'Fechar' : 'Mostrar mais!'"
              class="absolute! bottom-0 left-50% -translate-x-50% translate-y-50% tween-600"
              :class="{ 'rotate-180': showTop }"
              @click="showTop = !showTop"
            />
          </template>
        </Expandable>
      </div>
    </template>

    <template #left>
      <VotingList
        ref="votingList"
        v-model:loading="loading"
        :meeting-id="attrs.id"
        :meeting="meeting"
        :voting="voting"
        :socket="socket"
        :open="accordion[0]"
        @click="toggle(0)"
      />
    </template>

    <template #right>
      <VotersList
        v-model:loading="loading"
        :meeting-id="attrs.id"
        :meeting="meeting"
        :voting="voting"
        :socket="socket"
        :open="accordion[1]"
        @click="toggle(1)"
      />
    </template>

    <template #bottom>
      <TimeLineCounter
        v-if="onPresence || onVoting"
        class="tween-600"
        :class="{ 'translate-y-[calc(100%_+_40px)]': !voting.id && !onPresence }"
        :start="onPresence ? meeting.startRegisterPresence : voting.startDate"
        :end="onPresence ? meeting.endRegisterPresence : voting.endDate"
      />
    </template>
  </Page>
</template>

<route lang="yaml">
  meta:
    authenticated: true
    notGuest: true
</route>