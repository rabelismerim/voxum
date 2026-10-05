<script setup>
const props = defineProps({
  start: {
    type: String,
    default: () => (new Date(Date.now() - 24 * 60 * 60 * 1000)).toGMTString(),
  },
  end: {
    type: String,
    default: () => (new Date(Date.now() + 24 * 60 * 60 * 1000)).toGMTString(),
  },
})

let localStart = $ref(new Date(props.start))
let localEnd = $ref(new Date(props.end))
watchEffect(() => {
  localStart = new Date(props.start)
  localEnd = new Date(props.end)
})

function toHours(miliseconds) {
  const { floor } = Math
  const totalSeconds = floor(miliseconds / 1000)
  let hours = floor(totalSeconds / 3600)
  let minutes = floor((totalSeconds - (hours * 3600)) / 60)
  let seconds = totalSeconds - (hours * 3600) - (minutes * 60)

  if (hours < 10)
    hours = `0${hours}`
  if (minutes < 10)
    minutes = `0${minutes}`
  if (seconds < 10)
    seconds = `0${seconds}`
  return `${hours}:${minutes}:${seconds}`
}

const now = useNow()
const percentage = $computed(() => ((now.value - localStart) / (localEnd - localStart)))
const rest = $computed(() => toHours(Math.max(+localEnd - +now.value, 0)))
</script>

<template>
  <div class="relative">
    <Bar
      :percentage="percentage"
      :color="percentage < .7 ? 'secondary' : percentage < .9 ? 'warning' : 'negative'"
      class="h-3! rounded-0!"
    />
    <div
      class="absolute border-1 border--content/12 -top-10 text-white py-2 px-3 rounded-lg mb-2 tween-600 whitespace-nowrap flex items-center justify-center leading-3"
      :class="{
        '-translate-x-100%': percentage > .5,
        'bg-black/80 ': percentage < .9,
        'bg--error': percentage >= .9,
      }"
      :style="{ left: `${Math.max(Math.min(percentage, 1), 0) * 100}%` }"
    >
      {{ rest }}
    </div>
  </div>
</template>
