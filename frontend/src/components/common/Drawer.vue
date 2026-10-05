<script setup>
const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
  },
  position: {
    type: String,
    default: 'right', // 'right' || 'left'
  },
  hideTitle: {
    type: Boolean,
  },
  width: {
    type: Number,
    default: 250,
  },
})
const emit = defineEmits(['update:open', 'click'])

let isOpen = $ref(false)
watchEffect(() => {
  isOpen = props.open
})

function toggle() {
  emit('click')
  isOpen = !isOpen
  emit('update:open', isOpen)
}
</script>

<template>
  <div
    class="bg--base relative flex flex-nowrap overflow-y-hidden"
    :class="{ 'flex-row-reverse': position === 'left' }"
  >
    <div v-if="$slots.header && !hideTitle">
      <slot name="header" />
    </div>
    <div
      v-else-if="!hideTitle"
      class="flex flex-col py-4 px-2 gap-2 items-center cursor-pointer hover:bg--secondary/10 tween h-full"
      :class="{ 'color--secondary': isOpen }"
      @click="toggle"
    >
      <div class="flex items-center">
        <div
          class="w-6 h-6 rounded-full hover:bg--secondary/20 flex items-center justify-center tween-1000"
          :class="{ 'rotate-180': isOpen }"
        >
          <div
            class="w-5 h-5 text--secondary"
            :class="position === 'right' ? 'icon i-carbon-chevron-left' : 'icon i-carbon-chevron-right'"
          />
        </div>
      </div>
      <slot v-if="$slots.title" name="title" />
      <div
        v-else
        class="flex-1 font-bold"
        style="writing-mode: vertical-rl;text-orientation: mixed;"
      >
        {{ title }}
      </div>
    </div>

    <div
      class="grid overflow-x-hidden tween-600 h-full overflow-y-auto"
      :class="{ 'grid-cols-1': isOpen, 'grid-cols-0': !isOpen }"
    >
      <div class="min-w-0 h-full overflow-hidden">
        <div class="h-full" :style="{ minWidth: `${width}px` }">
          <slot v-if="$slots.content" name="content" />
          <div v-else class="overflow-y-auto overflow-x-hidden h-full">
            <slot />
          </div>
        </div>
      </div>
    </div>
    <slot name="append" v-bind="{ toggle, isOpen }" />
  </div>
</template>
