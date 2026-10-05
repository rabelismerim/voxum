<script setup>
const props = defineProps({
  open: {
    type: Boolean,
  },
  creditor: {
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
const emit = defineEmits(['update:creditor', 'update:open', 'success', 'close'])

let loading = $ref(false)
const form = ref(null)

const { socket } = useSocket({ url: 'V1/general' })

const classList = $computed(() => socket.value.channels?.classeList?.data ?? [])

const coinOptions = $computed(() => props.options?.coinOptions?.map(({ id, legend }) => ({ type: id, typeDisplay: legend })) || [])
const personOptions = $computed(() => props.options?.typePersonOptions?.map(({ id, legend }) => ({ label: legend, value: id })) || [])

let localCreditor = $ref(clone(props.creditor))
function clearCreditor() {
  localCreditor = clone(props.creditor)
}
watchEffect(() => {
  if (props.creditor)
    clearCreditor()
})

const name = $computed(() => `${localCreditor?.guest?.user?.firstName ?? ''} ${localCreditor?.guest?.user?.lastName ?? ''}`)
const legalNumber = $computed(() => localCreditor?.guest?.entity?.legalNumber)

async function onSubmit() {
  loading = true
  try {
    const creditor = clone(localCreditor)
    creditor.guest.user.email = creditor.email
    const result = await creditorsService.updateCreditor(creditor)
    if (result?.id) {
      notify({ message: 'Credor Atualizado com sucesso!' })
      emit('update:creditor', null)
      emit('update:open', false)
    }
  }
  catch (error) {
    print('ERROR ON UPDATING CREDITOR:', error)
  }
  finally {
    loading = false
  }
}

function onClose(value) {
  emit('update:open', value)
  if(value)
    return
  clearCreditor()
  form.value.resetValidation()
  emit('close')
}
</script>

<template>
  <Modal
    :title="`Editando Credor: ${name}`"
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
            v-model="localCreditor.email"
            class="col-span-4"
          />
          <QSelect
            v-model="localCreditor.typePerson"
            label="Tipo de Pessoa"
            :options="personOptions"
            emit-value
            map-options
            outlined
            dense
            :rules="[value => !!value || 'Este campo é obrigatório!']"
            class="col-span-2"
          />
          <InputSelect
            v-model="localCreditor.classeId"
            v-model:options="classList"
            label="Classe"
            :rules="[(value) => !!value || 'É um campo obrigatório']"
            :disable="loading"
            class="col-span-2"
          />
          <QSelect
            v-model="localCreditor.coin"
            :options="coinOptions"
            label="Moeda"
            outlined
            map-options
            option-label="typeDisplay"
            option-value="type"
            dense
            :rules="[value => !!value || 'Este campo é obrigatório!']"
            class="col-span-2"
          />
          <InputNumber
            v-model="localCreditor.creditValue"
            label="Valor do Crédito"
            class="col-span-2"
          />
          <InputNumber
            v-model="localCreditor.convertedValue"
            label="Valor Convertido"
            class="col-span-2"
          />
          <InputNumber
            v-model="localCreditor.contestedValue"
            label="Valor Contestado"
          />
          <InputNumber
            v-model="localCreditor.exchangeTax"
            label="Taxa de Câmbio"
          />
          <Toggle
            v-model="localCreditor.docOk"
            label="Documento Validado"
            class="col-span-2 justify-between mb-5"
          />
        </div>
        <div class="flex gap-3 items-center col-span-3 font-bold text-4 mb-2 px-4">
          <div>Representantes</div>
          <BtnIcon
            icon="i-carbon-add"
            class="rounded-full bg-slate/10! h-9! w-9!"
            type="button"
            tooltip="Adicionar Novo Representante"
            @click="localCreditor.representatives?.push({})"
          />
        </div>
        <div v-auto-animate="{ duration: 300 }" class="p-4">
          <div
            v-for="(representative, index) in localCreditor.representatives"
            :key="representative.id"
            class="flex gap-x-3"
          >
            <div class="flex flex-col gap-y-.5">
              <button
                :disabled="index === 0"
                class="rounded aspect-square h-5 bg-slate/20 hover:bg--secondary hover:color-white flex justify-center items-center disabled:bg-gray/10 disabled:hover:bg-gray/10 disabled:color-gray"
                type="button"
                @click="swapElements(localCreditor.representatives, index, index - 1)"
              >
                <div class="i-carbon-chevron-up" />
              </button>
              <button
                :disabled="index + 1 === localCreditor.representatives?.length"
                class="rounded aspect-square h-5 bg-slate/20 hover:bg--secondary disabled:bg-gray/10 disabled:hover:bg-gray/10 disabled:color-gray hover:color-white flex justify-center items-center"
                type="button"
                @click="swapElements(localCreditor.representatives, index, index + 1)"
              >
                <div class="i-carbon-chevron-down" />
              </button>
            </div>
            <div class="flex justify-center items-center font-bold text-xl w-10 h-10 bg-slate/10 color-slate-7 border-1 border-solid border-black/20 rounded">
              {{ index + 1 }}°
            </div>
            <div class="flex-1 gap-x-3">
              <QSelect
                v-model="localCreditor.representatives[index]"
                label="Representantes"
                :options="representatives"
                outlined
                dense
                use-input
                :rules="[value => !!value || 'Este campo é obrigatório!']"
              >
                <template #selected-item>
                  <div class="text-3">{{ representative?.fullName }}</div>
                </template>
                <template #option="{opt, itemProps}">
                  <QItem v-bind="itemProps">
                    <div>
                      <div class="font-semibold color--content/80">{{ opt?.fullName }}</div>
                      <div class="text-3">{{ formatLegalNumber(opt?.legalNumber) ?? '-' }}</div>
                    </div>
                  </QItem>
                </template>
                <template #no-option>
                  <div class="p-4">
                    Nenhum Representante disponível
                  </div>
                </template>
              </QSelect>
            </div>
            <BtnIcon
              type="button"
              icon="i-carbon-trash-can"
              color="negative"
              class="border-1 border--negative/50 border-solid rounded-1! h-10! w-10!"
              @click="localCreditor.representatives.splice(index, 1)"
            />
          </div>
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