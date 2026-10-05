<script setup>
import { ref, computed, watch, watchEffect } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
  },
  representative: {
    type: Object,
    default: () => ({}),
  },
  voting: {
    type: Object,
    default: () => ({}),
  },
  corporateMode: {
    type: Boolean,
  },
})

const emit = defineEmits(['update:open', 'update:representative', 'success', 'close'])

const { dialog } = useQuasar()

function cloneObj(obj) {
  if (!obj) return {}
  return typeof structuredClone === 'function'
    ? structuredClone(obj)
    : JSON.parse(JSON.stringify(obj))
}

function isSameObj(a, b) {
  return JSON.stringify(a) === JSON.stringify(b)
}

const loading = ref(false)
const localCreditor = ref(cloneObj(props.representative))

watchEffect(() => {
  localCreditor.value = cloneObj(props.representative)
})

const choices = computed(() => props.voting?.classChoice ?? [])
const classeNames = computed(() => choices.value.map(({ classe }) => classe))
const classeVoting = ref('')

const representativeName = computed(() => `${localCreditor.value?.guest?.user?.firstName ?? ''} ${localCreditor.value?.guest?.user?.lastName ?? ''}`)
const legalNumber = computed(() => props.representative?.guest?.entity?.legalNumber || '')

const useChoices = computed(() => {
  const localChoices = choices.value.reduce((acc, { choices: choiceItems, classe } = {}) => {
    choiceItems?.forEach((choice) => {
      const { value } = choice ?? {}
      if (!acc[value]) acc[value] = {}
      acc[value][classe] = choice.id
    })
    return acc
  }, {})

  return Object.entries(localChoices).map(([value, choicesMap]) => ({
    value,
    choices: choicesMap,
  }))
})

const filterBy = ref('')
const creditorsFilter = ref('notVoted')
const creditors = ref([])
const creditorsChoice = ref({})
const oldCreditorsChoice = ref({})
const creditorsErrors = ref({})
const creditorsCaveat = ref({})

const hasChanges = computed(() => !isSameObj(creditorsChoice.value, oldCreditorsChoice.value))

const separetedList = computed(() =>
  creditors.value.reduce(
    (acc, creditor, index) => {
      const { choice } = creditor
      const listType = choice ? 'voted' : 'notVoted'
      const newCreditor = {
        ...creditor,
        index: acc[listType].length,
        globalIndex: index,
        list: listType,
      }
      acc.all.push(newCreditor)
      acc[listType].push(newCreditor)
      return acc
    },
    { all: [], voted: [], notVoted: [] }
  )
)

const filteredCreditors = computed(() =>
  (creditorsFilter.value === 'all' ? separetedList.value.all : separetedList.value[creditorsFilter.value]).filter(
    ({ name, legalNumber: legNum }) =>
      [name, legNum].some(item => (item ?? '').toLowerCase().includes(filterBy.value.toLowerCase()))
  )
)

const totalCreditorCount = ref(0)
const continueLoading = ref(true)

async function loadCreditors(classe, notResetCreditorsFilter) {
  if (!props.representative?.id || !classe || loading.value) return

  if (!notResetCreditorsFilter) creditorsFilter.value = 'notVoted'
  selectedCreditor.value = null
  creditorsChoice.value = {}
  oldCreditorsChoice.value = {}
  creditorsErrors.value = {}
  creditors.value = []
  loading.value = true

  const limit = 20
  const getPage = async (page = 1) => {
    const { count, items } = await votingService.getRepresentativeCreditors({
      representativeId: props.representative?.id,
      votingId: props.voting?.id,
      offset: (page - 1) * 20,
      limit,
      classe,
    })
    await delay?.(0.5)
    for (const { id, choice, hasReservations } of items) {
      oldCreditorsChoice.value[id] = choice
      creditorsChoice.value[id] = choice
      creditorsCaveat.value[id] = hasReservations
    }
    return { count, items }
  }

  try {
    const { count, items } = await getPage()
    totalCreditorCount.value = count
    creditors.value.push(...items)
    for (let page = 2; page <= Math.ceil(count / limit); page++) {
      if (!continueLoading.value) break
      const { items: pageItems } = await getPage(page)
      creditors.value.push(...pageItems)
    }
  }
  catch (error) {
    console.error('ERROR ON LOADING CREDITORS:', error)
  }
  finally {
    loading.value = false
  }
}

const totalSelectedCount = computed(() => Object.values(creditorsChoice.value).filter(Boolean).length)

const hasChoosed = (creditor, choice) =>
  creditorsChoice.value[creditor.id] === (choice.choices?.[creditor?.classe?.description] ?? 'choice')

function selectChoice(creditor, choice) {
  if (isVoting.value) return
  creditorsChoice.value[creditor.id] = choice.choices?.[creditor?.classe?.description]
}

function clearAll(choice) {
  dialog({
    title: 'Confirmação',
    message: `Você deseja limpar todos para a opção "${choice?.value}"?${loading.value ? '\n(Será aplicado somente nos credores já carregados!)' : ''}`,
    ok: true,
    cancel: true,
  }).onOk(() => {
    const creditorIds = filteredCreditors.value.map(({ id }) => id)
    const choiceIds = Object.values(useChoices.value.find(({ value }) => value === choice.value)?.choices ?? {})
    Object.entries(creditorsChoice.value).forEach(([creditorId, choiceId]) => {
      if (creditorIds.includes(creditorId) && choiceIds.includes(choiceId)) {
        creditorsChoice.value[creditorId] = undefined
        creditorsCaveat.value[creditorId] = undefined
      }
    })
  })
}

function selectAll(choice) {
  dialog({
    title: 'Confirmação',
    message: `Você deseja selecionar todos para a opção "${choice?.value}"?${loading.value ? '\n(Será aplicado somente nos credores já carregados!)' : ''}`,
    ok: true,
    cancel: true,
  }).onOk(() => {
    filteredCreditors.value.forEach(({ id, classe }) => {
      creditorsChoice.value[id] = choice.choices?.[classe?.description]
    })
  })
}

const hasCaveat = creditor => creditorsCaveat.value[creditor.id] === true

function setCaveat(creditor) {
  if (creditorsChoice.value[creditor.id]) {
    creditorsCaveat.value[creditor.id] = !creditorsCaveat.value[creditor.id]
  }
}

const selectedCreditor = ref(null)
const votingEnded = computed(() => selectedCreditor.value?.globalIndex === totalCreditorCount.value - 1)
const isVoting = ref(false)

function votingBy() {
  dialog({
    title: `Votando por Representante na Classe: ${classeVoting.value}`,
    message: `Você confirma que o Representante "${representativeName.value}" requisitou esta ação?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    isVoting.value = true
    try {
      const creditorList = Object.entries(creditorsChoice.value)
      const method = props.corporateMode ? 'voteForRepresentative' : 'representativeVote'

      for (const [creditorId, choiceId] of creditorList) {
        if (!continueLoading.value) break

        selectedCreditor.value = separetedList.value.all.find(({ id }) => id === creditorId)

        if (oldCreditorsChoice.value[creditorId] === choiceId) continue
        const results = await votingService[method](
          props.representative.id,
          props.voting.meetingId,
          [{ creditorId, voteId: choiceId, hasReservations: creditorsCaveat.value[creditorId] }]
        )
        await delay?.(0.5)

        if (results?.[0]) {
          const creditorIndex = creditors.value.findIndex(({ id }) => id === creditorId)
          if (creditorIndex > -1) {
            Object.assign(creditors.value[creditorIndex], {
              choice: choiceId,
              hasReservations: creditorsCaveat.value[creditorId],
            })
          }
        }
      }

      notify?.({ message: `Votação na classe: (${classeVoting.value}) registrada com sucesso!` })
      loadCreditors(classeVoting.value, true)
      oldCreditorsChoice.value = cloneObj(creditorsChoice.value)
      isVoting.value = false
    }
    catch (error) {
      console.error('ERROR ON REGISTRING VOTING BY:', error)
    }
    finally {
      isVoting.value = false
    }
  })
}

watch(() => props.open, (value) => {
  if (value && props.voting?.id) {
    continueLoading.value = true
    classeVoting.value = classeNames.value[0]
    loadCreditors(classeVoting.value)
  }
})

async function clear() {
  selectedCreditor.value = null
  filterBy.value = ''
  creditorsFilter.value = 'notVoted'
  creditorsChoice.value = {}
  oldCreditorsChoice.value = {}
  creditorsErrors.value = {}
  creditorsCaveat.value = {}
  continueLoading.value = false
  creditors.value = []
  emit('update:representative', {})
  await delay?.(5)
}

function onModalClose(value) {
  clear()
  emit('update:open', value)
  if (!value) emit('close')
}
</script>

<template>
  <Modal
    :title="`Votando por ${representativeName}`"
    :subtitle="`${legalNumber?.length > 11 ? 'CNPJ' : 'CPF'}: ${formatLegalNumber(legalNumber)}`"
    :model-value="open"
    modal-class="max-w-250"
    :exit-confirmation="isVoting ? 'Ao sair durante a votação os votos não computados serão perdidos! Confirma a sua saída?' : undefined"
    @update:model-value="onModalClose"
    @close="emit('close')"
  >
    <template #side>
      <div class="w-full flex gap-2 justify-between items-center">
        <div class="flex gap-2 flex-nowrap">
          <div
            v-for="classe in classeNames"
            :key="classe"
            class="px-2 py-.6 text-3 bg-slate/20 rounded-full font-bold whitespace-nowrap"
            :class="{
              'bg--primary text-white': classe === classeVoting,
            }"
          >
            {{ classe }}
          </div>
        </div>
        <div class="flex gap-2">
          <BtnToggle
            v-model="creditorsFilter"
            :options="{
              all: 'Todos',
              voted: 'Votou',
              notVoted: 'Não Votou',
            }"
          />
          <SearchFilter
            v-model:search="filterBy"
            placeholder="Buscar por..."
            auto-size
            input-class="min-w-23!"
            :disabled="isVoting"
          />
        </div>
      </div>
    </template>

    <QLinearProgress v-if="loading" indeterminate color="secondary" class="absolute z-101 h-1.5 -translate-y-100%" />

    <QForm @submit="votingBy">
      <div
        v-if="creditors.length"
        class="relative grid gap-y-2 pb-4 lg:min-h-50 max-h-[calc(90vh-14.5rem)] overflow-y-auto"
        :style="{
          gridTemplateColumns: `minmax(150px,20%) repeat(${useChoices.length + 1}, 1fr)`,
          gridTemplateRows: '30px',
        }"
      >
        <div class="bg--base pl-3 pr-1 pb-1 sticky top-0 left-0 font-bold flex items-center z-101">
          Credor
        </div>

        <button
          v-for="choice in useChoices"
          :key="choice.value"
          type="button"
          class="bg--base px-1 pb-1 sticky top-0 font-bold flex justify-center items-center z-100 cursor-pointer whitespace-nowrap"
          :disabled="isVoting"
        >
          <div class="flex gap-1 flex-nowrap items-center">
            {{ choice.value }}
            <div class="i-tabler-chevron-down mt-1" />
          </div>
          <QMenu>
            <QList>
              <q-item clickable v-close-popup @click="selectAll(choice)">
                <q-item-section>Selecionar Todos</q-item-section>
              </q-item>
              <q-item clickable v-close-popup @click="clearAll(choice)">
                <q-item-section>Limpar</q-item-section>
              </q-item>
            </QList>
          </QMenu>
        </button>

        <div class="bg--base px-1 pb-1 sticky right-0 top-0 font-bold flex justify-center items-center z-100">
          Ressalva
        </div>

        <template v-for="creditor in filteredCreditors" :key="creditor.id">
          <div class="sticky left-0 pl-2 pr-1 text-3 xl:text-4 bg--base z-100">
            <div
              class="p-1 rounded-2 h-full"
              :class="{
                'bg--error/10 cursor-help': creditorsErrors[creditor.id],
              }"
            >
              <div class="font-bold">{{ creditor?.name }}</div>
              <div class="text-2 xl:text-3">{{ formatLegalNumber(creditor?.legalNumber) }}</div>
              <div class="text-2 xl:text-3">{{ formatMoney(creditor?.amount) }}</div>
              <QTooltip
                v-if="creditorsErrors[creditor.id]"
                anchor="center right"
                self="center left"
                class="bg--error"
              >
                {{ creditorsErrors[creditor.id] }}
              </QTooltip>
            </div>
          </div>

          <div
            v-for="choice in useChoices"
            :key="choice.value"
            :disabled="isVoting"
            class="px-1 min-w-20"
            @click="selectChoice(creditor, choice)"
          >
            <div
              class="rounded-2 h-full w-full cursor-pointer tween flex justify-center items-center text--content/30"
              :class="{
                'bg--primary/5': !hasChoosed(creditor, choice),
                'bg--secondary': hasChoosed(creditor, choice),
              }"
            >
              <div
                :class="{
                  'i-tabler-dots': !hasChoosed(creditor, choice),
                  'i-tabler-check': hasChoosed(creditor, choice),
                }"
              />
            </div>
          </div>

          <div class="px-1 sticky right-0 pr-2" @click="setCaveat(creditor)">
            <div
              :disabled="isVoting"
              class="rounded-2 h-full w-full cursor-pointer flex justify-center items-center text--content/30 backdrop-blur-lg"
              :class="{
                'bg-yellow/10': !hasCaveat(creditor),
                'bg-yellow': hasCaveat(creditor),
              }"
            >
              <div class="i-tabler-alert-triangle" />
            </div>
          </div>
        </template>

        <div
          v-if="isVoting && selectedCreditor?.list === creditorsFilter"
          class="absolute w-full h-full z-1000 px-1 pointer-events-none animate-pulse tween"
          :style="{
            gridColumn: `1/${useChoices.length + 3}`,
            gridRow: Array(2).fill((creditorsFilter === 'all' ? selectedCreditor.globalIndex : selectedCreditor?.index) + 2).join('/'),
          }"
        >
          <div class="bg--secondary/20 rounded-2 w-full h-[calc(100%+.5rem)] -my-1" />
        </div>

        <div
          v-if="!filteredCreditors.length"
          class="px-4 py-6 flex justify-center items-center text-center"
          :style="{
            gridColumn: `1/${useChoices.length + 3}`,
          }"
        >
          Nenhum credor listado nesse filtro...
        </div>
      </div>

      <div v-else-if="loading" class="px-4 py-6 lg:min-h-50 flex justify-center items-center text-center">
        Carregando a lista de Credores para essa Classe
      </div>

      <div v-else class="px-4 py-6 lg:min-h-50 flex justify-center items-center text-center">
        Nenhum credor nessa Classe para esse Representante
      </div>

      <div class="p-3 min-h-13.5 border-t-1 border--content/12 flex justify-between items-center">
        <div class="flex text-3 xl:text-5 gap-x-1">
          <div v-if="isVoting || votingEnded">Voto registrado:</div>
          <div v-else>Selecionados:</div>
          <div>{{ isVoting || votingEnded ? separetedList.voted?.length ?? 0 : totalSelectedCount }} de {{ totalCreditorCount }}</div>
          <div>credores</div>
        </div>

        <div class="flex-grow-1 flex gap-2 items-center justify-end flex-nowrap">
          <div v-if="loading && !isVoting" class="text-3 max-w-60 text-right text--error">
            Ações aplicadas aos Credores serão aplicadas somente à lista já carregada!
          </div>

          <BtnIcon
            type="button"
            outlined
            color="primary"
            icon="i-tabler-chevron-left"
            :disabled="classeNames.indexOf(classeVoting) === 0"
            @click="loadCreditors(classeVoting = classeNames[classeNames.indexOf(classeVoting) - 1])"
          />

          <BtnIcon
            type="button"
            outlined
            color="primary"
            icon="i-tabler-chevron-right"
            :disabled="classeNames.indexOf(classeVoting) === classeNames.length - 1"
            @click="loadCreditors(classeVoting = classeNames[classeNames.indexOf(classeVoting) + 1])"
          />

          <Btn
            v-if="(hasChanges && totalCreditorCount > 0) || separetedList.notVoted.length"
            label="Votar"
            loading-label="Registrando Voto..."
            :loading="isVoting"
            :disabled="totalSelectedCount !== totalCreditorCount || isVoting"
          />
        </div>
      </div>
    </QForm>
  </Modal>
</template>

<route lang="yaml">
meta:
  authenticated: true
  permissions: [can_manage_project]
</route>