<script setup>
const props = defineProps({
  user: {
    type: Object,
    default: () => ({}),
  },
  showDetail: {
    type: Boolean,
    default: false,
  },
})

const { user: currentUser } = useUser

const isCurrentUser = $computed(() => currentUser.value?.id === props.user?.id)
</script>

<template>
  <div class="flex items-center gap-3">
    <UserPicture :model-value="user" class="h-10 w-10 rounded-full" />
    <div class="flex flex-col">
      <div class="flex items-center gap-2">
        <span class="font-bold text-sm">{{ user.fullName || user.username || '-' }}</span>
        <StatusTag
          v-if="user.isStaff"
          label="Admin"
          color="#86bc25"
        />
        <StatusTag
          v-else-if="user.isUserGuest"
          label="Externo"
          color="#cccccc"
        />
        <StatusTag
          v-else
          label="Interno"
          color="#00a3e0"
        />
      </div>
      <span class="text-xs text-gray-500">{{ user.email || '-' }}</span>
      <div v-if="showDetail" class="text-xs text-gray-400 mt-1">
        <span v-if="isCurrentUser" class="font-semibold text-primary">(Você)</span>
      </div>
    </div>
  </div>
</template>