<script setup>
const props = defineProps({
  open: {
    type: Boolean,
  },
  representative: {
    type: Object,
    default: () => ({}),
  },
  options: {
    type: Object,
    default: () => ({}),
  },
  representatives: {
    type: Array,
    default: () => ([]),
  },
})
const emit = defineEmits(['update:representative', 'update:open', 'success', 'close'])

let loading = $ref(false)
const form = ref(null)

let localRepresentative = $ref(clone(props.representative))
function clearRepresentative() {
  localRepresentative = clone(props.representative)
}
watchEffect(() => {
  if (props.representative)
    clearRepresentative()
})

const name = $computed(() => `${localRepresentative?.guest?.user?.firstName ?? ''} ${localRepresentative?.guest?.user?.lastName ?? ''}`)
const legalNumber = $computed(() => localRepresentative?.guest?.entity?.legalNumber)

async function onSubmit() {
  loading = true
  try {
    const representative = clone(localRepresentative)
    representative.guest.user.email = representative.email
    const result = await creditorsService.updateCreditor(representative)
    if (result?.id) {
      notify({ message: 'Representante Atualizado com sucesso!' })
      emit('update:representative', null)
      emit('update:open', false)
    }
  }
  catch (error) {
    print('ERROR ON UPDATING REPRESENTATIVE:', error)
  }
  finally {
    loading = false
  }
}

function onClose(value) {
  emit('update:open', value)
  if(value)
    return
  clearRepresentative()
  form.value.resetValidation()
  emit('close')
}
</script>

<template>
  <Modal
    :title="`Editando Representante: ${name}`"
    :subtitle="`${String(legalNumber).length === 11 ? 'CPF' : 'CNPJ'} ${formatLegalNumber(legalNumber || 0)}`"
    :model-value="open"
    :loading="loading"
    modal-class="max-w-200"
    @update:model-value="onClose"
  >
    <QForm
      ref="form"
      @submit.prevent="onSubmit"
    >
      <div class="max-h-80vh overflow-y-auto">
        <div class="px-4 pt-4 grid grid-cols-6 gap-x-3">
          <InputText
            label="Email"
            v-model="localRepresentative.email"
            class="col-span-4"
          />
          <Toggle
            v-model="localRepresentative.docOk"
            label="Documento Validado"
            class="col-span-2 justify-between mb-5"
          />
        </div>
      </div>
      <div class="p-4 border-t-1 border--content/12 flex justify-between">
        <Btn
          label="Bloquear"
          type="button"
          color="negative"
          icon="i-carbon-error"
          outlined
        />
        <Btn
          label="Salvar"
          type="submit"
        />
      </div>
    </QForm>
  </Modal>
</template>