<script setup>
const props = defineProps({
  open: {
    type: Boolean,
  },
  meetingId: {
    type: String,
    required: true,
  },
})
const emit = defineEmits(['update:open', 'success', 'close'])

const form = ref()
let loading = $ref(false)

const nullRepresentative = reactive({
  fullName: '',
  email: '',
  legalNumber: '',
})

let newRepresentative = $ref(clone({ ...nullRepresentative }))
async function clear() {
  newRepresentative = clone(nullRepresentative)
  await delay(0.5)
  form.value.resetValidation()
}

async function onSubmit() {
  try {
    loading = true

    const { id, name } = await meetingService.createRepresentative(props.meetingId, newRepresentative)

    if (id) {
      notify({ id, message: 'Representante criado com sucesso!' })
      emit('success')
      emit('update:open', false)
      clear()
    }
  }
  catch (error) {
    await delay(0.01)
    print('ERROR ON CREATE REPRESENTATIVE:', error)
  }
  finally {
    loading = false
  }
}
function onModalClose(value) {
  clear()
  emit('update:open', value)
  if (!value)
    emit('close')
}

onMounted(() => {
})
</script>

<template>
  <Modal
    title="Novo Representante"
    :model-value="open"
    modal-class="max-w-180"
    @update:model-value="onModalClose"
  >
    <QForm ref="form" @submit.prevent="onSubmit">
      <div class="grid sm:grid-cols-2 gap-x-6 gap-y-2 px-6 py-3">
        <InputText
          v-model="newRepresentative.fullName"
          label="Nome"
          class="sm:col-span-2"
          :rules="[value => !!value || 'Este campo é obrigatório!']"
        />
        <InputText
          v-model="newRepresentative.email"
          label="E-mail"
          class="sm:col-span-1"
          :rules="[value => !!value || 'Este campo é obrigatório!']"
        />

        <InputText
          v-model="newRepresentative.legalNumber"
          label="Documento"
          class="sm:col-span-1"
          :rules="[value => !!value || 'Este campo é obrigatório!']"
        />
      </div>
      <div class="p-4 border-t-1 border--content/12 flex justify-end">
        <QLinearProgress
          v-if="loading"
          indeterminate
          color="secondary"
          class="absolute top-0 left-0"
          size="xs"
        />
        <Btn
          label="Criar"
          type="submit"
          loading-label="Criando Representante..."
          :loading="loading"
        />
      </div>
    </QForm>
  </Modal>
</template>
