<script setup>
const props = defineProps({
  date: {
    type: Object, // {day: [String] || true}
    default: () => ({}),
  },
  locale: {
    type: String,
    default: 'pt-BR',
  },
})

const {isMobile} = useAmbient()

let dateContext = $ref(dayjs())
const today = $ref(dayjs())
const days = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab']
const months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
const month = $computed(() => dateContext.format('M'))
const year = $computed(() => dateContext.format('YYYY'))
const currentMonth = $computed(() => months[+dateContext.format('M') - 1])
const daysInMonth = $computed(() => dateContext.daysInMonth())
const currentDate = $computed(() => dateContext.get('date'))
const firstDayOfMonth = $computed(() => dayjs(dateContext).subtract(currentDate - 1, 'days').day())

function addMonth() {
  dateContext = dayjs(dateContext).add(1, 'month')
}
function subtractMonth() {
  dateContext = dayjs(dateContext).subtract(1, 'month')
}
function isToday(day) {
  return dayjs(`${month}-${day}-${year}`).format('DD-MM-YYYY') === today.format('DD-MM-YYYY')
}
function isSelected(day) {
  return !!props.date[dayjs(`${month}-${day}-${year}`).format('DD-MM-YYYY')]
}
function getItems(day) {
  const items = props.date[dayjs(`${month}-${day}-${year}`).format('DD-MM-YYYY')]
  return items
}
function canSelectDate(day) {
  const date = dayjs(`${month}-${day}-${year}`)
  return date.isAfter(today) || isToday(day)
}

</script>

<template>
  <div class="calendar p-4 flex flex-col flex-nowrap">
    <div class="pb-3 flex items-center gap-3">
      <button class="cursor-pointer rounded-2 hover:bg--primary/10 text--content text-5" @click="subtractMonth">
        <div class="i-carbon-chevron-left"/>
      </button>
      <h5>{{ `${currentMonth} ${year}` }}</h5>
      <button class="cursor-pointer rounded-2 hover:bg--primary/10 text--content text-5" @click="addMonth">
        <div class="i-carbon-chevron-right"/>
      </button>
    </div>
    <ul class="p-0 pb-2 grid grid-cols-7 gap-1 list-none text-center">
      <li v-for="day in days" :key="day">
        {{ day }}
      </li>
    </ul>
    <ul class="p-0 grid grid-cols-7 gap-1 list-none text-center flex-1">
      <li v-for="(_, index) in firstDayOfMonth" :key="`blank-${index}`" />
      <li
        v-for="date in daysInMonth"
        :key="date"
        class="p-1 rounded-3 flex justify-center items-center"
      >
        <div
          class="h-8 flex justify-center items-center aspect-square rounded-full cursor-default"
          :class="{
            'bg--primary text-white cursor-help!': isSelected(date),
            'bg--primary text-white': isToday(date),
            'ring-3 ring-offset-1 ring--primary/30': isToday(date),
          }"
        >
          {{ date }}
          <QTooltip v-if="isSelected(date) && !isMobile()">
            <div>
              <div v-for="(item, index) in getItems(date)" :key="index">
                • {{ item }}
              </div>
            </div>
          </QTooltip>
        </div>
      </li>
    </ul>
  </div>
</template>
