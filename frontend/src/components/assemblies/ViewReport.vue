<script setup>
const props = defineProps({
  meeting: {
    type: Object,
    default: () => ({}),
  },
  voting: {
    type: Object,
    default: () => ({}),
  },
  height: {
    type: Number,
    default: 0,
  },
  valueKey: {
    type: String,
    default: 'value',
  },
})

const notNaN = num => Number.isNaN(num) ? 0 : num
</script>

<template>
  <Draw
    width="1123"
    :height="voting?.height"
    fill="#fff"
    class="h-80"
  >
    <TextBox
      model-value="Sistema Voxum"
      x="30"
      y="36"
      width="740"
      lines="1"
      font-size="20"
      font-family="Arial"
      bold
    />
    <TextBox
      :model-value="`Assembleia: ${meeting?.name ?? '...'} - ${meeting?.location?.description ?? '...'}`"
      x="30"
      y="80"
      width="880"
      lines="1"
      font-size="32"
      font-family="Arial"
    />
    <TextBox
      :model-value="`Data: ${meeting?.startDate ? dayjs(meeting.startDate).format('DD/MM/YYYY') : '...'}`"
      x="810"
      y="82"
      width="280"
      lines="1"
      font-size="20"
      font-family="Arial"
      align="right"
    />
    <TextBox
      :model-value="meeting?.description ?? '...'"
      x="30"
      y="130"
      width="740"
      lines="1"
      font-size="20"
      font-family="Arial"
    />
    <TextBox
      :model-value="voting?.description ?? '...'"
      x="30"
      y="180"
      width="1000"
      lines="2"
      font-size="30"
      bold
      font-family="Arial"
    />
    <g
      v-for="(result, index) in voting?.results ?? []"
      :key="index"
      :transform="`translate(${notNaN(30 + (index % 3) * 365)}, ${notNaN(260 + Math.floor(index / 3) * (voting.classeBoxSize + 20))})`"
    >
      <TextBox
        :model-value="result.name.toLowerCase() !== 'total' ? `Classe ${result.name}` : result.name"
        :bold="result.name.toLowerCase() === 'total'"
        font-size="20"
      />
      <g
        v-for="(option, optionIndex) in result.choices"
        :key="optionIndex"
        :transform="`translate(0, ${notNaN(40 + optionIndex * 30)})`"
      >
        <TextBox
          :model-value="option.option"
          width="150"
          lines="2"
          font-size="12"
          :bold="result.name.toLowerCase() === 'total'"
        />
        <Rect
          x="160"
          width="117"
          height="16"
          color="#000"
          opacity=".05"
        />
        <Rect
          x="160"
          :width="117 * option[valueKey]"
          height="16"
          border="#000"
          border-width=".5"
          border-opacity=".2"
        />
        <TextBox
          :model-value="`${notNaN(option[valueKey] * 100).toFixed(2)}%`"
          x="270"
          width="55"
          lines="1"
          font-size="12"
          align="right"
        />
      </g>
    </g>
    <TextBox
      :model-value="voting?.isCount
        ? '* Dados baseados em quantidade de credores.'
        : '* Dados baseados no montante total de Créditos.'"
      x="30"
      :y="(voting?.height ?? 0) - 35"
      width="880"
      lines="1"
      font-size="12"
      font-family="Arial"
      bold
    />
  </Draw>
</template>