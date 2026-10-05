<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  users: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:model-value', 'success'])

const { hasPermissions } = useUser

const form = ref(null)
const loading = ref(false)
const editingUser = ref({})
const tab = ref('pending')
const groups = ref([])

function cloneObj(obj) {
  if (!obj) return {}
  return typeof structuredClone === 'function'
    ? structuredClone(obj)
    : JSON.parse(JSON.stringify(obj))
}

const pendingUsers = computed(() => props.users?.filter(({ isActive }) => isActive === false) ?? [])
const rejectedUsers = computed(() => props.users?.filter(({ isActive }) => isActive === false) ?? [])

async function loadGroups() {
  try {
    if (!hasPermissions?.('change_user', 'view_group')) return
    groups.value = await usersService.getUserGroups()
  }
  catch (error) {
    console.error('ERROR ON LOADING GROUPS on RequestModal:', error)
  }
}

function editUser(user) {
  editingUser.value = cloneObj(user)
}

function clear() {
  emit('update:model-value', false)
  tab.value = 'pending'
  editingUser.value = {}
}

async function onAuthorize() {
  const activeUser = { ...editingUser.value, isActive: true }

  if (!form.value || !form.value.validate) return

  const isValid = await form.value.validate()
  if (!isValid) return

  loading.value = true

  try {
    const { id, isActive } = await usersService.updateUser(activeUser)

    if (id && isActive) {
      clear()
      emit('success')
      notify?.({ message: 'O Usuário foi ativado com sucesso!' })
    }
  }
  catch (error) {
    console.error('ERROR ON ACCEPTING THE USER REQUEST:', error)
  }
  finally {
    loading.value = false
  }
}

async function onReject(user) {
  const targetUser = user || editingUser.value
  const updatedUser = { ...targetUser, isActive: false }

  if (!targetUser?.isActive && user) return

  loading.value = true
  try {
    const { id, isActive } = await usersService.updateUser(updatedUser)

    if (id && !isActive) {
      clear()
      emit('success')
      notify?.({ message: 'O Usuário foi ignorado!' })
    }
  }
  catch (error) {
    console.error('ERROR ON REJECTING THE USER REQUEST:', error)
  }
  finally {
    loading.value = false
  }
}

onMounted(() => {
  loadGroups()
})
</script>

<template>
  <Modal
    :model-value="modelValue"
    :title="editingUser?.email ? 'Cadastrar Usuário' : 'Solicitações'"
    :loading="loading"
    modal-class="max-w-120 request-modal"
    @close="clear"
  >
    <div v-if="editingUser?.email">
      <QForm
        ref="form"
        @submit="onAuthorize"
      >
        <div class="max-h-100 overflow-y-auto px-6 pt-4">
          <div class="flex mb-6">
            <UserCell :model-value="editingUser" />
          </div>
          <InputSelect
            v-model="editingUser.group"
            label="Permissão"
            :rules="[(value) => !!value || 'Este campo é obrigatório!']"
            :options="groups"
          />
        </div>
        <div class="flex justify-end gap-3 p-4 border-t-1 border--content/12">
          <Btn
            label="Voltar"
            outlined
            type="button"
            @click="editingUser = {}"
          />
          <Btn
            type="submit"
            label="Cadastrar"
          />
        </div>
      </QForm>
    </div>
    <div v-else>
      <QTabs
        v-model="tab"
        align="left"
        active-color="secondary"
      >
        <QTab
          name="pending"
          label="Pendentes"
        >
          <span class="bg--secondary/12 color--secondary rounded-full px-2 font-bold">
            {{ pendingUsers?.length }}
          </span>
        </QTab>
        <QTab
          name="rejected"
          label="Ignoradas"
        />
      </QTabs>
      <QTabPanels v-model="tab" animated class="shadow-2 rounded-borders">
        <QTabPanel name="pending">
          <div
            v-if="pendingUsers?.length === 0"
            class="p-4 text-center"
          >
            Sem Usuários Pendentes no momento...
          </div>
          <div
            v-for="(user, pendingIndex) in pendingUsers"
            v-else
            :key="user.id"
            class="flex py-3 px-1 items-center"
            :class="{ 'border-b-1 border--black/12': pendingIndex < pendingUsers.length - 1 }"
          >
            <UserCell :model-value="user" />
            <div class="flex flex-1 justify-end gap-2">
              <Btn
                label="Ignorar"
                outlined
                :disabled="loading"
                @click="onReject(user)"
              />
              <Btn
                label="Aceitar"
                :disabled="loading"
                @click="editUser(user)"
              />
            </div>
          </div>
        </QTabPanel>

        <QTabPanel name="rejected">
          <div
            v-if="rejectedUsers?.length === 0"
            class="p-4 text-center"
          >
            Sem Usuários Ignorados no momento...
          </div>
          <div
            v-for="(user, rejectedIndex) in rejectedUsers"
            v-else
            :key="user.id"
            class="flex py-3 items-center"
            :class="{ 'border-b-1 border--black/12': rejectedIndex < rejectedUsers.length - 1 }"
          >
            <UserCell :model-value="user" />
            <div class="flex flex-1 justify-end gap-2">
              <Btn
                label="Aceitar"
                :disabled="loading"
                @click="editUser(user)"
              />
            </div>
          </div>
        </QTabPanel>
      </QTabPanels>
    </div>
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