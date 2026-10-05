<script setup>
const props = defineProps({
  rows: {
    type: Array,
    default: () => [],
  },
  columns: {
    type: Array,
    default: () => [],
  },
  bordered: {
    type: Boolean,
  },
  title: {
    type: String,
  },
  tooltip: {
    type: String,
  },
})
const emit = defineEmits(['update:rows'])

let localRows = $ref([])
watchEffect(() => {
  localRows = clone(props.rows)
})
function updateTable() {
  emit('update:rows', clone(localRows))
}

const countLines = $ref(0)
function addRows() {
  const values = range(0, countLines - 1).map(() => {
    const attrs = props.columns
      .filter(({ required }) => required)
    const obj = {}
    attrs.forEach(({ type, field, name }) => {
      const defaultValue = (() => {
        if (['float', 'integer'].includes(type))
          return 0
        if (type === 'boolean')
          return false
        return ''
      })()
      set(field || name, obj, defaultValue)
    })
    return obj
  })
  localRows.push(...values)
  updateTable()
}

const isRequired = ({ required }) => required && [value => value !== undefined || 'Campo obrigatório!']
</script>

<template>
  <div class="flex items-center justify-between px-4">
    <div class="flex items-center gap-2">
      <span v-if="title" class="font-bold text-xl">{{ title }}</span>
      <span v-if="tooltip" class="color--error text-xs">{{ tooltip }}</span>
    </div>
    <AddLines
      v-model="countLines"
      @add-lines="addRows"
    />
  </div>
  <QTable
    :rows="localRows"
    :columns="columns"
    :pagination="{ rowsPerPage: 0 }"
    hide-pagination
    flat
    :bordered="bordered"
    class="custom-table"
  >
    <template #body="properties">
      <QTr :props="properties">
        <QTd
          v-for="column in properties.cols"
          :key="column.id"
          :style="(column?.editable) && column?.type !== 'boolean'
            ? (column?.editable) && column?.type === 'text'
              ? 'min-width: 200px; width: 10%' : 'min-width: 150px; width: 10%'
            : '' "
        >
          <div
            class="flex justify-center items-center"
            :class="{
              'is-loading': properties.row.loading,
              // 'has-error': statusLabel(properties.row?.status) === 'Erro',
            }"
          >
            <button
              v-if="column.name === 'delete' && table.many"
              class="cursor-pointer bg--error h-9 w-9 rounded-1 border-1 border-red-8 flex justify-center items-center"
              :disable="column.disabled"
              @click.stop="remove(table.values, properties.row, properties.rowIndex, table)"
            >
              <div class="i-carbon-trash-can bg-white" />
            </button>
            <div v-else-if="column.label === 'Status'" :class="{ 'has-error': properties.row.status === 'ERROR' }">
              <StatusTag
                v-if="properties.row.status"
                :label="statusLabel(properties.row.status)"
                :color="statusColors[properties.row.status]"
                :tooltip="properties.row[column.field]"
              />
            </div>
            <div v-else-if="!column.editable" class="row justify-center">
              <span v-if="column.type === 'float'">{{ formatNumber(get(column.field, properties.row), column.decimals) || '-' }}</span>
              <span v-else>{{ get(column.field, properties.row) || '-' }}</span>
            </div>
            <QInput
              v-else-if="column.type === 'float' || column.type === 'integer'"
              v-model="properties.row[column.field]"
              :rules="isRequired(column)"
              class="flex-1"
              type="number"
              outlined
              dense
              :disable="column.disabled"
              @update:model-value="value => { if (column.type === 'integer') (properties.row[column.field] = Math.round(value)) }"
              @paste.prevent="onPaste($event, table.values, column.field, column.type, properties.rowIndex)"
            />
            <InputDate
              v-else-if="column.type === 'date'"
              v-model="properties.row[column.field]"
              :rules="isRequired(column)"
              class="flex-1"
              :disable="column.disabled"
              @paste.prevent="onPaste($event, table.values, column.field, column.type, properties.rowIndex)"
            />
            <div v-else-if="column.type === 'boolean'" class="row justify-center">
              <QToggle
                v-model="properties.row[column.field]"
                :disable="column.disabled"
                class="flex-1"
              />
            </div>
            <QInput
              v-else
              v-model="properties.row[column.field]"
              :rules="isRequired(column)"
              class="flex-1"
              outlined
              dense
              :disable="column.disabled"
              @paste.prevent="onPaste($event, table.values, column.field, column.type, properties.rowIndex)"
            />
          </div>
        </QTd>
      </QTr>
    </template>
  </QTable>
</template>

<style>
.calculation-details .q-panel.scroll,
.custom-table .q-table__middle.scroll {
  overflow-y: hidden;
}
.custom-table .q-field--with-bottom {
  padding: 0;
}
.custom-table .q-field--error .q-field__bottom {
  padding: 0;
}
.custom-table .q-field--error .q-field__bottom div[role=alert] {
  background-color: var(--q-negative);
  color: #fff;
  padding: 4px;
  display: flex;
  justify-content: center;
  border-radius: 0 0 4px 4px;
  margin-top: -2px;
}
.custom-table tr:has(.has-error) {
  background-color: hsla(var(--error,0,0%,0%),0.05)
}
.custom-table td.q-td {
  padding: 8px 6px;
  width: 0.1%;
  white-space: nowrap;
}
.custom-table tr td:first-child {
  padding-left: 16px;
}
.custom-table tr td:last-child {
  padding-right: 8px;
}
.calculations-credits {
  background: transparent;
}
.calculations-credits .q-tab-panel {
padding: 0;
}
</style>
