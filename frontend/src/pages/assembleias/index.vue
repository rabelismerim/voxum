<script setup>
let loading = $ref(false)
const showNewAsssembly = $ref(false)
const showCalendar = $ref(true)
const calendarIcon = $computed(() =>
  showCalendar ? 'i-tabler-calendar-off' : 'i-tabler-calendar-month',
)

const { login, hasPermissions } = useUser

const filterBy = $ref('')
let assemblies = $ref([])
const dates = $computed(() => assemblies.reduce((acc, meeting) => {
  const day = dayjs(meeting.startDate).format('DD-MM-YYYY')
  if (!acc[day])
    acc[day] = []
  acc[day].push(meeting.name)
  return acc
}, {}))

const exportReports = $ref({
  meeting: null,
  show: false,
})
function selectToExport(meeting) {
  exportReports.show = true
  exportReports.meeting = meeting
}

const editing = $ref({
  meeting: null,
  show: false,
})
function selectToEdit(meeting) {
  editing.show = true
  editing.meeting = meeting
}

const suspending = $ref({
  meeting: null,
  show: false,
})
function selectToSuspend(meeting) {
  suspending.show = true
  suspending.meeting = meeting
}

const statusColors = {
  i: '#007db3', // iniciada
  e: '#007cb0', // encerrada
  a: '#cccccc', // agendada
  t: '#DA291C', // atrasada
  r: '#FFD700', // reagendada
}

const columns = [
  {
    name: 'name',
    field: 'name',
    label: 'Nome',
    align: 'left',
    sortable: true,
    classes: 'max-w-50 overflow-hidden text-ellipsis',
  },
  {
    name: 'description',
    field: 'description',
    label: 'Descrição',
    align: 'left',
    sortable: true,
    format: value => value || '-',
    classes: 'max-w-50 overflow-hidden text-ellipsis',
  },
  {
    name: 'location',
    field: 'location',
    label: 'Local',
    align: 'left',
    sortable: true,
    format: value => value ?? '-',
    classes: 'min-w-1',
  },
  {
    name: 'start',
    field: 'startDate',
    label: 'Data de Início',
    align: 'left',
    sortable: true,
    format: value => formatDate(value, '@DD/@MM/@YYYY @HH:@mm'),
  },
  {
    name: 'situation',
    field: 'situationDisplay',
    label: 'Situação',
    sortable: true,
    align: 'right',
  },
  {
    name: 'status',
    field: 'statusDisplay',
    label: 'Status',
    sortable: true,
    align: 'right',
  },
  {
    name: 'actions',
    field: 'actions',
    label: 'Ações',
    headerClasses: 'text-right w-14',
  },
]

async function loadAssemblies() {
  loading = true
  try {
    const meetingsResult = await meetingService.getMeetings()
    const meetingsMap = meetingsResult.reduce((acc, meeting) => {
      acc[meeting.id] = meeting
      return acc
    }, {})
    const groups = await meetingService.getGroups()
    const groupedMeetingIds = new Set(
      groups.flatMap(({ meetings = [] }) => meetings.map(({ id }) => id)),
    )
    const groupedAssemblies = groups
      .filter(({ meetings }) => meetings?.length)
      .map(({ meetings = [] }) => {
        const [current, ...history] = meetings
          .sort(({ order: a }, { order: b }) => a < b ? 1 : -1)
          .map(({ id }) => meetingsMap[id])
        return {
          ...current,
          history,
        }
      })
    const ungroupedAssemblies = meetingsResult
      .filter(({ id }) => !groupedMeetingIds.has(id))
      .map(meeting => ({ ...meeting, history: [] }))
    assemblies = [...groupedAssemblies, ...ungroupedAssemblies]
  }
  catch (error) {
    print('ERROR ON LOAD ASSEMBLIES:', error)
  }
  finally {
    loading = false
  }
}

function redirectToAssembly(colName, row) {
  if (['status', 'actions'].includes(colName))
    return
  router.push(`/assembleias/${row.id}`)
}

const { loadLocations } = useLocations()

onMounted(() => {
  login()
  loadLocations().catch(error => print('ERROR ON LOAD LOCATIONS:', error))
  loadAssemblies()
})
</script>

<template>
  <Page :loading="loading">
    <div class="px-4 md:w-94% max-w-400 min-w-60 mx-auto py-8 flex flex-nowrap overflow-x-auto w-full">
      <div class="flex-1 flex flex-col flex-nowrap overflow-x-hidden">
        <Header
          :title="`Assembleias (${assemblies?.length || 0})`"
          sub-tittle="teste"
          class="mb-4"
        >
          <template #side>
            <ReloadBtn tooltip="Recarregar a Lista de Assembleias" @click="loadAssemblies" />
          </template>
          <SearchFilter
            v-model:search="filterBy"
            auto-size
          />
          <BtnIcon
            :icon="calendarIcon"
            color="primary"
            filled
            :tooltip="showCalendar ? 'Esconder' : 'Mostrar'"
            class="hidden lg:flex!"
            @click="showCalendar = !showCalendar"
          />
        </Header>
        <QTable
          :rows="assemblies"
          :columns="columns"
          :filter="filterBy"
          :rows-per-page-options="[5, 10, 15, 20, 25]"
          row-key="id"
          flat
          bordered
          class="flex-1 min-w-0 max-w-[calc(100vw-2rem)]"
        >
          <template #header="props">
            <QTr :props="props">
              <QTh auto-width />
              <QTh
                v-for="col in props.cols"
                :key="col.name"
                :props="props"
              >
                {{ col.label }}
              </QTh>
            </QTr>
          </template>

          <template #body="props">
            <QTr :props="props">
              <QTd auto-width>
                <div
                  v-if="props.row?.history?.length > 0"
                  class="cursor-pointer w-8 h-8 rounded-full bg--secondary/20 hover:bg--secondary/50 text--secondary hover:text-white flex items-center justify-center tween"
                  :class="{ 'rotate-180': props.expand }"
                  @click="props.expand = !props.expand"
                >
                  <div class="icon i-carbon-chevron-down w-6 h-6" />
                </div>
              </QTd>

              <QTd
                v-for="col in props.cols"
                :key="col.name"
                :props="props"
                :class="{
                  'cursor-pointer': !['status', 'actions'].includes(col.name),
                }"
                @click="redirectToAssembly(col.name, props.row)"
              >
                <BtnIcon
                  v-if="col.name === 'actions'"
                  flat
                  color="primary"
                  icon="i-carbon-overflow-menu-vertical"
                  class="rounded-full"
                  @click.stop
                >
                  <QMenu>
                    <QList class="min-w-max max-w-80vw">
                      <QItem v-close-popup clickable>
                        <QItemSection @click="selectToExport(props.row)">
                          Exportar Relatórios
                        </QItemSection>
                      </QItem>
                      <QItem v-close-popup clickable>
                        <QItemSection
                          v-if="hasPermissions('can_manage_project')"
                          @click="selectToEdit(props.row)"
                        >
                          Editar Assembleia
                        </QItemSection>
                      </QItem>
                      <QItem v-close-popup clickable>
                        <QItemSection
                          v-if="hasPermissions('can_manage_project')"
                          @click="selectToSuspend(props.row)"
                        >
                          Arquivar Assembleia
                        </QItemSection>
                      </QItem>
                    </QList>
                  </QMenu>
                </BtnIcon>
                <div
                  v-else-if="col.name === 'status'"
                  class="flex justify-end"
                >
                  <StatusTag
                    :label="props.row.statusDisplay"
                    :color="statusColors[props.row?.status?.toLowerCase()]"
                  />
                </div>
                <span v-else>
                  {{ col.value }}
                </span>
              </QTd>
            </QTr>
            <QTr v-show="props.expand" :props="props">
              <QTd colspan="100%" class="py-1! pr-1! pl-12! bg-slate/20!">
                <QTable
                  :rows="props.row.history"
                  :columns="columns"
                  :filter="filterBy"
                  :rows-per-page-options="[5, 10, 15, 20, 25]"
                  row-key="id"
                  flat
                  class="custom-inline-table flex-1 min-w-0 border--content/12 border-1 rounded-lg"
                  hide-bottom
                  @row-click="(_, row) => redirectToAssembly(null, row)"
                >
                  <template #body-cell-status="props">
                    <QTd :props="props">
                      <div class="flex justify-end">
                        <StatusTag
                          :label="props.value"
                          :color="statusColors[props.row?.status?.toLowerCase()]"
                        />
                      </div>
                    </QTd>
                  </template>

                  <template #body-cell-actions="props">
                    <QTd
                      :props="props"
                      class="flex justify-end"
                    >
                      <BtnIcon
                        flat
                        color="primary"
                        icon="i-carbon-overflow-menu-vertical"
                        class="rounded-full"
                        @click.stop
                      >
                        <QMenu>
                          <QList class="min-w-25">
                            <QItem v-close-popup clickable>
                              <QItemSection @click="selectToExport(props.row)">
                                Exportar Relatórios
                              </QItemSection>
                            </QItem>
                            <QItem v-close-popup clickable>
                              <QItemSection
                                v-if="hasPermissions('can_manage_project')"
                                @click="selectToEdit(props.row)"
                              >
                                Editar Assembleia
                              </QItemSection>
                            </QItem>
                          </QList>
                        </QMenu>
                      </BtnIcon>
                    </QTd>
                  </template>
                </QTable>
              </QTd>
            </QTr>
          </template>
        </QTable>
      </div>
      <Drawer
        hide-title
        :open="showCalendar"
        class="tween-600 bg-transparent hidden lg:block"
        :class="{ 'ml-4': showCalendar, 'opacity-0': !showCalendar }"
      >
        <div class="w-full bg--base rounded-1 border--content/12 border-1 mt-14.5">
          <Calendar :date="dates" class="h-full max-h-120 min-h-92" />
        </div>
      </Drawer>
    </div>

    <NewMeeting
      v-model="showNewAsssembly"
      @success="loadAssemblies"
    />
    <EditMeeting
      v-model="editing.show"
      :meeting="editing.meeting"
      @success="editing.meeting = null; loadAssemblies()"
    />
    <SuspendMeeting
      v-model="suspending.show"
      :meeting="suspending.meeting"
      @success="suspending.meeting = null; loadAssemblies()"
    />
    <ExportReports
      v-model:open="exportReports.show"
      v-model:meeting="exportReports.meeting"
    />

    <template #top>
      <div class="bg--base border-b-1 border--content/12">
        <div class="flex justify-between items-center gap-x-8 gap-y-2 px-4 py-2 max-w-400 mx-auto">
          <div class="flex gap-8">
            <BackButton />
            <Breadcrumbs :links="[{ label: 'Assembleias' }]" />
          </div>
          <Btn
            label="Nova Assembleia"
            tooltip="Criar uma nova Assembleia"
            @click="showNewAsssembly = true"
          />
        </div>
      </div>
    </template>
  </Page>
</template>

<style lang="scss">
.custom-inline-table {
  tr {
    height: 2rem !important;
    th {
      padding-block: 0;
    }
    th:last-child {
      padding-right: 10px !important;
    }
  }

  td:last-child {
    padding-right: 12px !important;
  }
}
</style>

<route lang="yaml">
  meta:
    authenticated: true
    notGuest: true
</route>