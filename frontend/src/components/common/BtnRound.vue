<script setup>
const props = defineProps({
  icon: {
    type: String,
    default: 'i-carbon-home',
  },
  label: {
    type: String,
  },
})
const emit = defineEmits(['click'])

const isIconLibrary = props.icon.startsWith('i-') && !props.icon.includes('/')
const {baseUrl} = useAmbient()
</script>

<template>
  <button
    class="group flex flex-col gap-4 items-center text-xl font-bold color--primary"
    @click="emit('click', $event)"
  >
    <div class="h-24 w-24 flex justify-center items-center bg--primary group-hover:bg--secondary p-4 rounded-full tween">
      <div
        v-if="isIconLibrary"
        :class="icon"
        class="color-white text-40px"
      />
      <Img
        v-else
        :src="`${baseUrl}/${icon}`"
        class="h-full"
      />
    </div>
    <div
      v-if="label"
      class="group-hover:color--secondary tween"
    >
      {{ label }}
    </div>
  </button>
</template>
