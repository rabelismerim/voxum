<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
  },
  meeting: {
    type: Object,
    default: () => ({}),
  },
  title: {
    type: String,
  },
})

const emit = defineEmits(['update:model-value', 'update:meeting', 'success'])

let loading = $ref(false)
const form = ref()

const {locations, addLocation} = useLocations()

const nullMeeting = {
  locationId: undefined,
  description: '',
  name: '',
  startDate: '',
  endDate: '',
  status: '',
  statusQuorum: '',
}
let localMeeting = $ref(clone(nullMeeting))
watchEffect(() => {
  localMeeting = clone(props.meeting ?? nullMeeting)
  localMeeting.locationId = locations.value?.find(({ description }) => description === localMeeting?.location || description === localMeeting?.location?.description)?.id
})
async function clear() {
  localMeeting = clone(nullMeeting)
  await delay(0.5)
  form.value.resetValidation()
}

async function onSubmit() {
  try {
    loading = true
    const { id, name } = await meetingService.updateMeeting(localMeeting)
    if (id) {
      notify({ id, message: `Assembleia ${name} editada com sucesso!` })
      emit('success')
      emit('update:model-value', false)
      clear()
    }
  }
  catch (error) {
    await delay (0.01)
    print('ERROR ON EDIT ASSEMBLY:', error)
  }
  finally {
    loading = false
  }
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    :title="`Editando Assembleia ${meeting?.name ?? '...'}` "
    modal-class="max-w-200"
    @update:model-value="(value) => emit('update:model-value', value)"
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
          :max="localMeeting.endDate"
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
