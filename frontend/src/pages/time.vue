<script setup>
const router = useRouter()
const { login, hasPermissions } = useUser

const form = ref(null)
const tab = $ref('all')

let filterBy = $ref('internal')
let showEditUser = $ref(false)
let editingUser = $ref({})
function editUser(evt, user) {
  if(user.isUserGuest) return
  editingUser = user
  showEditUser = true
}

const {
  loading: loadingUsers,
  items: users,
  get: loadUsers,
  pagination: usersPagination,
  updatePagination: updateUsersPagination,
} = usersService.getUsers()
updateUsersPagination({ userInternal: 'true', filterColumn: 'first_name' })

const editPaginationFilter = value => {
  if(['internal', 'guest'].includes(value)) {
    updateUsersPagination({
      userInternal: value === 'internal' ? 'true' : 'false',
      status: undefined,
    })
    return
  }
  if(value === 'pending') {
    updateUsersPagination({
      userInternal: undefined,
      isActive: false,
    })
    return
  }
}

const groups = $computed(() => {
  return [
    { label: 'Todos', value: 'all' },
  ]
})

const columns = [
  {
    name: 'first_name',
    field: 'fullName',
    label: 'Usuário',
    required: true,
    align: 'left',
    sortable: true,
  },
  {
    name: 'email',
    field: 'email',
    label: 'Email',
    align: 'left',
    sortable: true,
    format: value => value || '-',
  },
  {
    name: 'permission',
    field: 'groups',
    label: 'Permissão',
    align: 'left',
    format: value => value?.length ? value?.map(({ name }) => name)?.join(',\n') : '-',
  },
  {
    name: 'is_staff',
    field: 'isStaff',
    label: 'Acesso Admin',
    align: 'center',
    style: 'width: 100px',
    format: value => value ? '✔️' : '-',
  },
  {
    name: 'is_user_guest',
    field: 'isUserGuest',
    label: 'Usuário Externo',
    align: 'center',
    style: 'width: 100px',
    format: value => value ? '✔️' : '-',
  },
  {
    name: 'status',
    field: 'isActive',
    label: 'Ativo',
    align: 'left',
    style: 'width: 100px',
    sortable: true,
  },
]

const isLoading = $computed(() => loadingUsers.value)

onMounted(async () => {
  await login()
  if (!hasPermissions('can_manage_project')) {
    throwError({
      id: 'SUBMIT_ERROR',
      message: 'Você não tem permissão para acessar esta página!',
    })
    router.push('/')
  }
  else {
    loadUsers()
  }
})
</script>

<template>
  <Page :loading="isLoading">
    <div class="w-full px-4 md:px-8 py-8 max-w-400 min-w-60 mx-auto">
      <Header title="Time">
        <template #side>
          <ReloadBtn
            tooltip="Recarregar a Lista de Usuários"
            @click="loadUsers"
          />
        </template>
      </Header>

      <TabFilter
        :model-value="tab"
        :items="groups"
      >
        <div class="flex flex-nowrap gap-2">
          <BtnToggle
            v-model="filterBy"
            class="h-9"
            :options="{
              internal: 'Interno',
              guest: 'Externo',
              pending: 'Convite'
            }"
            @update:modelValue="editPaginationFilter"
          />
          <SearchFilter
            v-model:search="usersPagination.filterBy"
            v-model:field="usersPagination.filterColumn"
            auto-size
            :options="{
              first_name: 'Nome',
              email: 'Email',
            }"
          />
        </div>
      </TabFilter>

      <QTable
        v-model:pagination="usersPagination"
        class="my-header-table"
        :columns="columns"
        :rows="users"
        :rows-per-page-options="[5, 10, 15, 20, 25]"
        row-key="id"
        flat
        bordered
        @row-click="editUser"
        @request="updateUsersPagination($event?.pagination)"
      >
        <template #body-cell-name="props">
          <QTd :props="props">
            <div class="flex no-wrap items-center gap-3 font-bold py-2">
              <UserPicture :model-value="props.row" class="h-9 w-9 rounded-1 mr-2" />
              <div class="font-medium">
                <div class="text-lg font-bold">
                  {{ props.row?.fullName }}
                </div>
              </div>
            </div>
          </QTd>
        </template>

        <template #body-cell-status="props">
          <QTd :props="props">
            <div class="flex">
              <StatusTag
                :label="props.row.isActive ? 'Ativo' : 'Inativo'"
                :color="props.row.isActive ? '#86bc25' : '#cccccc'"
              />
            </div>
          </QTd>
        </template>
      </QTable>
    </div>

    <EditUser
      v-model:open="showEditUser"
      v-model:user="editingUser"
      :form-ref="form"
      @success="loadUsers"
    />

    <template #top>
      <div class="flex justify-between items-center px-4 py-2 bg--base border-b-1 border--content/12">
        <div class="w-full px-4 md:px-8 flex gap-8 max-w-400 min-w-60 mx-auto">
          <BackButton />
          <Breadcrumbs :links="[{ label: 'Assembleias', url: '/assembleias' }, { label: 'Time' }]" />
        </div>
      </div>
    </template>
  </Page>
</template>

<route lang="yaml">
meta:
  authenticated: true
  notGuest: true
  permissions: [can_manage_project]
</route>