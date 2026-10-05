<script setup>
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      fullName: '',
      email: '',
      picture: '',
    }),
  },
})
</script>

<template>
  <div class="mr-3">
    <UserPicture :model-value="modelValue" class="h-9 w-9" />
  </div>
  <div>
    <div class="font-bold">
      {{ modelValue.fullName }}
    </div>
    <div>
      {{ modelValue.email }}
    </div>
  </div>
</template>
