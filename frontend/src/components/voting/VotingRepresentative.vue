<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  meeting: {
    type: Object,
    default: () => ({}),
  },
  representative: {
    type: Object,
    default: () => ({}),
  },
  qualifiedCreditors: {
    type: Array,
    default: () => [],
  },
  voting: {
    type: Object,
    default: () => ({}),
  },
  disabled: {
    type: Boolean,
  },
})

const emit = defineEmits(['update:open', 'update:representative', 'success', 'close'])

const { dialog } = useQuasar()

const loading = ref(false)

const creditors = computed(() =>
  props.qualifiedCreditors.map(
    ({ id, ableToVote, guest, classe, recovering, presence, typePerson, typePersonDisplay, creditValue, online }) => ({
      id,
      username: guest?.user?.username,
      name: `${guest?.user?.firstName ?? ''} ${guest?.user?.lastName ?? ''}`,
      email: guest?.user?.email,
      legalNumber: guest?.entity?.legalNumber,
      isRepresentative: guest?.entity?.isRepresentative,
      isCreditor: !guest?.entity?.isRepresentative,
      isActive: guest?.user?.isActive,
      creditValue,
      ableToVote,
      typePerson: {
        type: typePerson,
        description: typePersonDisplay,
      },
      classe: {
        id: classe?.id,
        description: classe?.description,
      },
      recovering: {
        id: recovering?.id,
        name: recovering?.name,
      },
      presence: {
        isPresent: presence?.isPresent,
        isAccredited: presence?.isAccredited,
        online,
      },
    })
  )
)

const useChoices = computed(() => {
  const localChoices = (props.voting?.qualifiedRepresentative ?? []).reduce(
    (acc, { choices: choiceItems, classe } = {}) => {
      choiceItems?.forEach((choice) => {
        const { value } = choice ?? {}
        if (!acc[value]) acc[value] = {}
        acc[value][classe] = choice.id
      })
      return acc
    },
    {}
  )
  return Object.entries(localChoices).map(([value, choicesMap]) => ({
    value,
    choices: choicesMap,
  }))
})

const classeNames = computed(() =>
  [...new Set(creditors.value.map(({ classe }) => classe?.description))].sort()
)

const classeVoting = ref('')

watch(
  () => props.voting,
  (value) => {
    classeVoting.value = value?.qualifiedRepresentative?.[0]?.name ?? ''
  },
  { immediate: true }
)

const filterBy = ref('')
const creditorsFilter = ref('notVoted')
const creditorsChoice = ref({})
const oldCreditorsChoice = ref({})
const creditorsErrors = ref({})
const creditorsCaveat = ref({})

function isSameObj(a, b) {
  return JSON.stringify(a) === JSON.stringify(b)
}

const hasChanges = computed(() => !isSameObj(creditorsChoice.value, oldCreditorsChoice.value))

const separetedList = computed(() =>
  creditors.value
    .filter(({ classe }) => classe?.description === classeVoting.value)
    .reduce(
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
    ({ name, legalNumber }) =>
      [name, legalNumber].some(item => (item ?? '').toLowerCase().includes(filterBy.value.toLowerCase()))
  )
)

const totalCreditorCount = computed(() => creditors.value.length)
const totalSelectedCount = computed(() => Object.values(creditorsChoice.value).filter(Boolean).length)

const hasChoosed = (creditor, choice) =>
  creditorsChoice.value[creditor.id] === (choice.choices?.[creditor?.classe?.id] ?? 'choice')

function selectChoice(creditor, choice) {
  creditorsChoice.value[creditor.id] = choice.choices?.[creditor?.classe?.id]
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
      creditorsChoice.value[id] = choice.choices?.[classe?.id]
    })
  })
}

const hasCaveat = creditor => creditorsCaveat.value[creditor.id] === true

function setCaveat(creditor) {
  if (creditorsChoice.value[creditor.id]) {
    creditorsCaveat.value[creditor.id] = !creditorsCaveat.value[creditor.id]
  }
}

const isVoting = ref(false)
const showVoteRepresentative = ref(false)

async function votingBy() {
  showVoteRepresentative.value = true
  isVoting.value = true
}
</script>

<template>
  <div v-if="creditors.length" class="w-[calc(100vw-2rem)] max-w-390">
    <div class="flex flex-col items-start mb-4 font-bold">
      <div class="flex gap-2 mt-2">
        Tipo de Votação
        <div class="px-2 py-.6 text-3 bg--primary/20 rounded-full font-bold whitespace-nowrap">
          {{ voting.typeDisplay }}
        </div>
      </div>
      <div class="text-6 leading-7 md:text-9 md:leading-11">
        {{ voting.description }}
      </div>
    </div>

    <div class="w-full flex gap-2 justify-between items-center">
      <div class="flex gap-2">
        <div
          v-for="classe in classeNames"
          :key="classe"
          class="px-2 py-.6 text-3 bg-gray/20 rounded-full font-bold whitespace-nowrap cursor-pointer"
          :class="{
            'bg--primary/20': classe === classeVoting,
          }"
          @click="classeVoting = classe"
        >
          {{ classe }}
        </div>
      </div>
      <SearchFilter
        v-model:search="filterBy"
        placeholder="Buscar por credor..."
        class="md:max-w-40"
        grow
        input-class="min-w-29!"
        :disabled="!creditors.length || isVoting || disabled"
      />
    </div>

    <QForm
      class="bg--base border-1 border--content/12 rounded-md overflow-hidden pt-2 mt-4"
      @submit="votingBy"
    >
      <div
        v-if="creditors.length"
        class="relative grid gap-y-2 pb-4 lg:min-h-50 max-h-[calc(90vh-24rem)] overflow-y-auto"
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
          :disabled="!meeting?.id || isVoting || disabled"
          class="bg--base px-1 pb-1 sticky top-0 font-bold flex justify-center items-center z-100 cursor-pointer whitespace-nowrap"
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
          <div
            class="sticky left-0 pl-2 pr-1 text-3 xl:text-4 bg--base z-100"
            :class="{
              'border-yellow border-l-4': hasCaveat(creditor),
            }"
          >
            <div
              class="p-1 rounded-2 h-full flex flex-col gap-.5 items-start"
              :class="{
                'bg--error/10 cursor-help': creditorsErrors[creditor.id],
              }"
            >
              <div class="font-bold">{{ creditor?.name }}</div>
              <div class="text-2.5 xl:text-3.5">{{ formatLegalNumber(creditor?.legalNumber) }}</div>
              <div class="text-2.5 xl:text-3.5 inline">{{ formatMoney(creditor?.creditValue) }}</div>
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

          <button
            v-for="choice in useChoices"
            :key="choice.value"
            type="button"
            class="px-1 min-w-20"
            :disabled="!meeting?.id || isVoting || disabled"
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
          </button>

          <button
            type="button"
            class="px-1 pr-2"
            :disabled="!meeting?.id || isVoting || disabled"
            @click="setCaveat(creditor)"
          >
            <div
              class="rounded-2 h-full w-full cursor-pointer flex justify-center items-center text--content/30 backdrop-blur-lg"
              :class="{
                'bg-yellow/10': !hasCaveat(creditor),
                'bg-yellow': hasCaveat(creditor),
              }"
            >
              <div class="i-tabler-alert-triangle" />
            </div>
          </button>
        </template>

        <div
          v-if="!filteredCreditors.length"
          class="px-4 py-6 flex justify-center items-center text-center"
          :style="{
            gridColumn: `1/${useChoices.length + 3}`,
          }"
        >
          Você não representa credores desta Classe...
        </div>
      </div>

      <div v-else-if="loading" class="px-4 py-6 lg:min-h-50 flex justify-center items-center text-center">
        Carregando a lista de Credores para essa Classe
      </div>

      <div v-else class="px-4 py-6 lg:min-h-50 flex justify-center items-center text-center">
        Nenhum credor nessa Classe para esse Representante
      </div>

      <div class="p-3 min-h-13.5 border-t-1 border--content/12 flex justify-between items-center">
        <div class="text-3">
          <div class="flex xl:text-5 gap-x-1">
            <div>Selecionados:</div>
            <div>{{ totalSelectedCount }} de {{ totalCreditorCount }}</div>
            <div>credores</div>
          </div>
          <div class="text--negative">
            Você precisa selecionar todos os credores de todas as classes para enviar o seu voto!
          </div>
        </div>

        <div class="flex-grow-1 flex gap-2 items-center justify-end flex-nowrap">
          <BtnIcon
            type="button"
            outlined
            color="primary"
            icon="i-tabler-chevron-left"
            :disabled="classeNames.indexOf(classeVoting) === 0"
            @click="classeVoting = classeNames[classeNames.indexOf(classeVoting) - 1]"
          />
          <BtnIcon
            type="button"
            outlined
            color="primary"
            icon="i-tabler-chevron-right"
            :disabled="classeNames.indexOf(classeVoting) === classeNames.length - 1"
            @click="classeVoting = classeNames[classeNames.indexOf(classeVoting) + 1]"
          />
          <Btn
            label="Votar"
            loading-label="Registrando Voto..."
            :loading="isVoting"
            :disabled="totalSelectedCount !== totalCreditorCount || isVoting || disabled"
            tooltip="Você precisa selecionar todos os credores de todas as classes para votar"
          />
        </div>
      </div>
    </QForm>

    <VoteRepresentative
      v-model:open="showVoteRepresentative"
      :meeting="meeting"
      :voting="voting"
      :creditor-votings="creditorsChoice"
      :creditor-caveats="creditorsCaveat"
      :choice-options="useChoices"
      @cancel="isVoting = false"
    />
  </div>

  <div v-else>
    <div class="p-8 mt-8 text-center font-bold text-3xl color-gray">
      Votação em Andamento, acompanhe pelo Zoom
    </div>
  </div>
</template>

<route lang="yaml">
meta:
  authenticated: true
  permissions: [can_manage_project]
</route>