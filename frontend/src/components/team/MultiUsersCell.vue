<script setup>
const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
})

const { isMobile } = useAmbient()
</script>

<template>
  <div v-if="items && items.length > 0" class="flex gap-2">
    <UserTag :model-value="items[0]" />
    <div
      v-if="items.length > 1"
      class="flex items-center no-wrap rounded-full px-3 py-.5 border-1 border-gray/20 bg-gray/20 whitespace-nowrap cursor-help"
    >
      + {{ items.length - 1 }}
      <QTooltip v-if="!isMobile()">
        <div class="flex max-w-100 justify-start items-center gap-2 ml-4 m-2">
          <UserTag
            v-for="(user, index) in items"
            :key="user.id || index"
            :model-value="user"
            transparent
          />
        </div>
      </QTooltip>
    </div>
  </div>
</template>