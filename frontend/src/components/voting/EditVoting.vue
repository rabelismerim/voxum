<script setup>
import { ref, watchEffect, onMounted } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  meetingId: {
    type: String,
    default: '',
  },
  voting: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:open', 'update:voting', 'success', 'close'])

const classList = ref([])
const loading = ref(false)

const defaultVoting = {
  description: '',
  type: 'S',
  classList: [],
  choices: ['Sim', 'Não'],
}

function cloneObj(obj) {
  if (!obj) return {}
  return typeof structuredClone === 'function'
    ? structuredClone(obj)
    : JSON.parse(JSON.stringify(obj))
}

const localVoting = ref(cloneObj(props.voting ?? defaultVoting))

async function loadClassList() {
  try {
    classList.value = await meetingService.getMappedClasses()
  }
  catch (error) {
    console.error('ERROR ON LOAD CLASSES:', error)
  }
}

function clearVoting() {
  const voting = cloneObj(props.voting)
  voting.classList = voting.classChoice?.map(
    ({ classe: classeName }) => classList.value.find(({ label }) => classeName === label)?.value
  ) ?? []
  voting.choices = voting.classChoice?.flatMap(({ choices }) => choices.map(({ value }) => value)) ?? ['Sim', 'Não']
  localVoting.value = voting
}

watchEffect(() => {
  if (props.voting && Object.keys(props.voting).length > 0) {
    clearVoting()
  }
})

const addChoice = () => {
  if (!localVoting.value.choices) localVoting.value.choices = []
  localVoting.value.choices.push(`Opção ${localVoting.value.choices.length + 1}`)
}

const removeChoice = (index) => {
  localVoting.value.choices.splice(index, 1)
}

async function createVoting() {
  loading.value = true
  try {
    const result = await votingService.update({ ...localVoting.value, meetingId: props.meetingId })
    if (result?.id) {
      notify?.({ message: 'Votação Editada com sucesso!' })
      emit('success')
      emit('update:open', false)
    }
  }
  catch (error) {
    console.error('ERROR ON EDITING VOTING:', error)
  }
  finally {
    loading.value = false
  }
}

function onModalClose(value) {
  clearVoting()
  emit('update:open', value)
  if (!value) emit('close')
}

const typeOptions = [
  { label: 'Assunto', value: 'S' },
  { label: 'Escolha', value: 'C' },
]

onMounted(() => {
  loadClassList()
})
</script>

<template>
  <Modal
    title="Editando votação"
    :model-value="open"
    modal-class="max-w-180"
    @update:model-value="onModalClose"
  >
    <QForm @submit="createVoting">
      <div class="p-4 grid grid-cols-3 gap-x-4">
        <InputText
          v-model="localVoting.description"
          label="Descrição"
          class="col-span-2"
          :rules="[value => !!value || 'Este campo é obrigatório!']"
        />
        <QSelect
          v-model="localVoting.type"
          label="Tipo"
          :options="typeOptions"
          outlined
          dense
          emit-value
          map-options
          :rules="[value => !!value || 'Este campo é obrigatório!']"
          @update:model-value="localVoting.choices = ['Sim', 'Não']"
        />
        <QSelect
          v-model="localVoting.classList"
          label="Classes"
          :options="classList"
          use-chips
          multiple
          outlined
          dense
          emit-value
          map-options
          :rules="[value => !!value?.length || 'Este campo é obrigatório!']"
          class="col-span-3"
          @update:model-value="localVoting.choices = ['Sim', 'Não']"
        />

        <div class="flex gap-3 items-center col-span-3 font-bold text-4 mb-2">
          <div>Opções</div>
          <BtnIcon
            v-if="localVoting.type === 'C'"
            icon="i-carbon-add"
            class="rounded-full bg-slate/10! h-9! w-9!"
            type="button"
            tooltip="Adicionar Nova Opção"
            @click="addChoice"
          />
        </div>

        <div class="col-span-3 grid grid-cols-2 gap-x-4">
          <InputText
            v-for="(choice, index) in localVoting.choices"
            :key="index"
            v-model="localVoting.choices[index]"
            :label="localVoting.type === 'S' ? (index === 0 ? 'Afirmativa' : 'Negativa') : `Opção ${index + 1}`"
            :rules="[value => !!value || 'Este campo é obrigatório!']"
          >
            <BtnIcon
              v-if="localVoting.type === 'C'"
              icon="i-carbon-trash-can"
              class="h-9! min-w-9! mt-.5 translate-x-2.5"
              type="button"
              color="error"
              tooltip="Apagar opção"
              @click="removeChoice(index)"
            />
          </InputText>
        </div>
      </div>

      <div class="p-3 border-t-1 border--content/12 flex justify-end">
        <Btn
          label="Salvar"
          loading-label="Criando Votação..."
          :loading="loading"
        />
      </div>
    </QForm>
  </Modal>
</template>