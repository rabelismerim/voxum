<script setup>
const { baseUrl } = useAmbient()
const user = useUser.user
</script>

<template>
  <nav class="flex flex-nowrap bg-black h-14 pl-3 md:pl-8 md:pr-8 justify-between items-center sticky top-0 z-100">
    <div class="flex items-center w-38 md:w-auto">
      <Img :src="`${baseUrl}/logo/voxum.svg`" :height="24" />
    </div>
    <div class="flex flex-nowrap h-full items-center gap-2 md:gap-5">
      <UserProfile v-if="user?.id" />
      <Img :src="`${baseUrl}/logo/app.svg`" :height="24" />
      <Img
        :src="`${baseUrl}/logo/digital-lab-dark.svg`"
        :height="32"
        class="hidden lg:block"
      />
    </div>
  </nav>
</template>