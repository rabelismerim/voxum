<script setup>
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      fullName: '',
      email: '',
      pictureUrl: '',
      userpicture: '',
    }),
  },
  initialsClass: {
    type: String,
  },
})

const {routerBaseUrl, apiHost, baseUrl} = useAmbient()

const imageOrigin = $computed(() => props.modelValue?.pictureUrl ?? props.modelValue?.userPicture)
const imageSrc = $computed(() => `${apiHost}${imageOrigin}`)
</script>

<template>
  <div class="rounded-1 overflow-hidden">
    <Img
      v-if="imageOrigin"
      :src="imageSrc"
      class="w-full h-full object-cover"
      :error-image="`${baseUrl}/fallback/user.svg`"
    />
    <div
      v-else
      class="bg-gray-2 rounded-1 flex justify-center color-slate-6 items-center text-4 h-full"
      :class="initialsClass"
    >
      {{ getInitials(modelValue.fullName) }}
    </div>
  </div>
</template>
