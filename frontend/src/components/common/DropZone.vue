<script setup>
const props = defineProps({
  types: {
    type: Array,
  },
})
const emit = defineEmits(['drop'])

const dropZoneRef = ref(null)
const input = ref(null)

function onSelectFiles(newFiles) {
  const files = Array.isArray(newFiles) ? newFiles : [...(input.value || { files: [] }).files]
  const filteredFiles = files
    .filter(({ name }) => (props.types?.length || 0) > 0
      ? props?.types?.some(type => name.endsWith(`.${type}`))
      : true)
  if (filteredFiles?.length === 0)
    return

  emit('drop', filteredFiles)
  input.value.value = ''
}
const { isOverDropZone } = useDropZone(dropZoneRef, onSelectFiles)
</script>

<template>
  <label ref="dropZoneRef" class="relative cursor-pointer flex flex-col w-full min-h-200px border-1 border--content/20 border-dashed justify-center items-center mt-6 rounded-1">
    <div class="flex flex-col gap-4 justify-center items-center">
      <div class="i-carbon-document-add text-5xl text--content/30" />
      <div>Clique ou arraste seus arquivos aqui!</div>
    </div>
    <input ref="input" type="file" multiple class="hidden" @change="onSelectFiles">
    <div v-if="isOverDropZone" class="absolute inset-0 bg--primary/20" />
  </label>
</template>
