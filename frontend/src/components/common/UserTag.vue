<script setup>
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      name: '',
      email: '',
      picture: '',
    }),
  },
  transparent: {
    type: Boolean,
  },
})
const {isMobile} = useAmbient()
</script>

<template>
  <div
    class="flex items-center no-wrap gap-2 rounded-full pl-1 pr-3 py-.5 whitespace-nowrap cursor-help"
    :class="{ 'border-1 border-gray/20 bg-gray/20': !transparent }"
  >
    <UserPicture :model-value="modelValue" class="h-5 w-5 rounded-full" initials-class="text-2 font-bold" />
    <div class="font-bold">
      {{ modelValue?.fullName || '-' }}
    </div>
    <QTooltip v-if="!isMobile()">
      <div class="flex flex-col gap-2 text-sm pt-2 justify-center items-center">
        <UserPicture :model-value="modelValue" class="h-16 w-16 rounded-1" />
        <div class="font-bold">
          {{ modelValue?.fullName || '-' }}
        </div>
        <div>{{ modelValue?.email || '-' }}</div>
      </div>
    </QTooltip>
  </div>
</template>
