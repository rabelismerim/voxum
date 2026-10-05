<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  meetingId: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['update:open', 'success', 'close'])

const form = ref(null)
const loading = ref(false)
const classList = ref([])

const defaultVoting = {
  description: '',
  type: 'S',
  classes: [],
  choices: [],
}

function cloneObj(obj) {
  if (!obj) return {}
  return typeof structuredClone === 'function'
    ? structuredClone(obj)
    : JSON.parse(JSON.stringify(obj))
}

const localVoting = ref(cloneObj(defaultVoting))

async function clearVoting() {
  localVoting.value = cloneObj(defaultVoting)
  if (classList.value.length > 0) {
    localVoting.value.classes = classList.value.map(({ value }) => value)
  }
  await delay?.(0.5)
  form.value?.resetValidation()
}

const addChoice = () => {
  localVoting.value.choices.push(`Opção ${localVoting.value.choices.length + 1}`)
}

const removeChoice = (index) => {
  localVoting.value.choices.splice(index, 1)
}

async function createVoting() {
  loading.value = true
  try {
    const result = await votingService.create({ ...localVoting.value, meetingId: props.meetingId })
    if (result) {
      notify?.({ message: 'Votação criada com sucesso!' })
      emit('success')
      emit('update:open', false)
      await delay?.(0.5)
      clearVoting()
    }
  }
  catch (error) {
    console.error('ERROR ON CREATING NEW VOTING:', error)
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

async function loadClassList() {
  try {
    classList.value = await meetingService.getMappedClasses()
    localVoting.value.classes = classList.value.map(({ value }) => value)
  }
  catch (error) {
    console.error('ERROR ON LOAD CLASSES:', error)
  }
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
    title="Nova votação"
    :model-value="open"
    modal-class="max-w-180"
    @update:model-value="onModalClose"
  >
    <QForm ref="form" @submit="createVoting">
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
          @update:model-value="localVoting.choices = localVoting.type === 'C' ? ['Opção 1', 'Opção 2'] : []"
        />
        <QSelect
          v-model="localVoting.classes"
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
        />

        <div v-if="localVoting.type === 'C'" class="flex gap-3 items-center col-span-3 font-bold text-4 mb-2">
          <div>Opções</div>
          <BtnIcon
            icon="i-carbon-add"
            class="rounded-full bg-slate/10! h-9! w-9!"
            type="button"
            tooltip="Adicionar Nova Opção"
            @click="addChoice"
          />
        </div>

        <div v-if="localVoting.type === 'C'" class="col-span-3 grid grid-cols-2 gap-x-4">
          <InputText
            v-for="(choice, index) in localVoting.choices"
            :key="index"
            v-model="localVoting.choices[index]"
            :label="`Opção ${index + 1}`"
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
          label="Criar"
          loading-label="Criando Votação..."
          :loading="loading"
        />
      </div>
    </QForm>
  </Modal>
</template>