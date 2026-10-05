<script setup>
import { ref, watchEffect, onMounted } from 'vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  user: {
    type: Object,
    default: () => ({}),
  },
  closeDisable: {
    type: Boolean,
    default: false,
  },
  formRef: {
    type: [Object, Array, String],
    default: null,
  },
})

const emit = defineEmits(['update:open', 'update:user', 'success'])

const form = ref(null)
const loading = ref(false)
const editingUser = ref({})
const tab = ref('pending')
const groups = ref({})

// Função auxiliar segura para clonagem profunda
function cloneObj(obj) {
  if (!obj) return {}
  return typeof structuredClone === 'function'
    ? structuredClone(obj)
    : JSON.parse(JSON.stringify(obj))
}

watchEffect(() => {
  editingUser.value = cloneObj(props.user)
})

function clear() {
  emit('update:open', false)
  emit('update:user', cloneObj(props.user))
  tab.value = 'pending'
}

async function onEdit() {
  if (!form.value) return
  const isValid = await form.value.validate()
  if (!isValid) return

  loading.value = true

  try {
    const { id } = await usersService.updateUser({
      ...editingUser.value,
      isActive: editingUser.value?.isActive?.id ?? editingUser.value?.isActive,
      group: editingUser.value?.group?.id ?? editingUser.value?.group,
    })
    if (id) {
      clear()
      emit('success')
      notify?.({ message: 'O Usuário foi alterado com sucesso!' })
    }
  }
  catch (error) {
    console.error('ERROR ON ACCEPTING THE USER REQUEST:', error)
  }
  finally {
    loading.value = false
  }
}

async function loadGroups() {
  try {
    const result = await usersService.getUserGroups()
    groups.value = result.reduce((acc, group) => {
      if (group.typeGroup === 'G') {
        acc[group.id] = group.name
      }
      return acc
    }, {})
  }
  catch (error) {
    console.error('ERROR ON LOADING GROUPS ON (EditUser):', error)
  }
}

onMounted(() => {
  loadGroups()
})
</script>

<template>
  <Modal
    :model-value="open"
    title="Editando Usuário"
    modal-class="max-w-120 request-modal"
    :close-disable="closeDisable"
    :loading="loading"
    @close="clear"
  >
    <QForm
      ref="form"
      @submit="onEdit"
    >
      <div class="max-h-100 overflow-y-auto px-6 pt-4">
        <div class="flex mb-6">
          <UserCell :model-value="editingUser" />
        </div>
        <Select
          v-model="editingUser.isActive"
          label="Status"
          :rules="[(value) => value !== undefined || 'Este campo é obrigatório!']"
          :options="{
            true: 'Ativo',
            false: 'Inativo',
          }"
        />
        <Select
          v-model="editingUser.group"
          label="Permissão"
          :rules="[(value) => value !== undefined || 'Este campo é obrigatório!']"
          :options="groups"
        />
      </div>
      <div class="flex justify-end gap-3 p-4 border-t-1 border--content/12">
        <Btn
          type="submit"
          label="Salvar"
        />
      </div>
    </QForm>
  </Modal>
</template>

<style>
.request-modal .q-tab__content {
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 8px;
}
.request-modal .q-tab-panels {
  box-shadow: none;
}
</style>