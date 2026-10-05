<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
  },
  title: {
    type: String,
  },
})

const emit = defineEmits(['update:modelValue', 'success'])

let loading = $ref(false)
const form = ref()

const nullMeeting = {
  locationId: undefined,
  description: '',
  name: '',
  startDate: (new Date()).toISOString(),
  endDate: (new Date()).toISOString(),
  statusQuorum: '',
}
let localMeeting = $ref(clone(nullMeeting))
async function clear() {
  localMeeting = clone(nullMeeting)
  await delay(0.5)
  form.value.resetValidation()
}

const {locations, addLocation} = useLocations()

async function onSubmit() {
  try {
    loading = true
    const { id, name } = await meetingService.postMeeting(localMeeting)
    if (id) {
      notify({ id, message: `Novo: ${name} criado com sucesso!` })
      emit('success')
      emit('update:modelValue', false)
      clear()
    }
  }
  catch (error) {
    await delay (0.01)
    print('ERROR ON CREATE ASSEMBLY:', error)
  }
  finally {
    loading = false
  }
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    title="Cadastro de Assembleia"
    modal-class="max-w-200"
    @update:model-value="(value) => emit('update:modelValue', value)"
    @close="clear"
  >
    <QForm ref="form" @submit.prevent="onSubmit">
      <div class="grid sm:grid-cols-6 gap-x-6 gap-y-2 px-6 py-3">
        <InputText
          v-model="localMeeting.name"
          label="Nome da Assembleia"
          class="col-span-2 sm:col-span-4"
          :rules="[(value) => !!value || 'É um campo obrigatório']"
        />
        <InputSelect
          v-model="localMeeting.locationId"
          v-model:options="locations"
          label="Localização"
          :to-add="addLocation"
          class="col-span-2"
          :rules="[(value) => !!value || 'É um campo obrigatório']"
          :disable="loading"
        />
        <InputText
          v-model="localMeeting.description"
          label="Descrição"
          class="col-span-2 sm:col-span-3"
          :rules="[
            (value) => !!value || 'É um campo obrigatório',
            (value) => value.length <= 150 || 'Tamanho máximo é de 150 caracteres!',
          ]"
        />
        <InputDateTime
          v-model="localMeeting.startDate"
          label="Data de Início"
          :rules="[(value) => !!value || 'É um campo obrigatório']"
          class="sm:col-span-3"
        />
      </div>

      <div class="relative flex justify-end gap-2 p-3 border-t-1 border--content/12">
        <QLinearProgress
          v-if="loading"
          indeterminate
          color="secondary"
          class="absolute top-0 left-0"
          size="xs"
        />
        <Btn
          label="Concluir"
          type="submit"
          loading-label="Criando Assembleia..."
          :loading="loading"
        />
      </div>
    </QForm>
  </Modal>
</template>
