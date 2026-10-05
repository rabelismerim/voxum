<script setup>
const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
  },
  icon: {
    type: String,
    default: 'i-carbon-chevron-right',
  },
  hideIcon: {
    type: Boolean,
  },
  iconRight: {
    type: String,
  },
  hideTitle: {
    type: Boolean,
  },
  showDivider: {
    type: Boolean,
  },
  titleClass: {
    type: String,
    default: 'p-4',
  },
  color: {
    type: String,
    default: 'base',
  },
  contentClass: {
    type: String,
    default: 'p-4',
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
  <div class="relative max-w-full" :style="{ background: `hsl(var(--${color}))` }">
    <div v-if="$slots.header && !hideTitle">
      <slot name="header" />
    </div>
    <div
      v-else-if="!hideTitle"
      class="flex hover:bg--secondary/10 gap-2 items-center cursor-pointer tween-600 overflow-hidden max-w-full"
      :class="[{ 'color--secondary': isOpen }, titleClass]"
      @click="toggle"
    >
      <div
        v-if="icon && !hideIcon"
        class="flex items-center"
      >
        <div
          class="w-8 h-8 mr-1 rounded-full hover:bg--secondary/20 flex items-center justify-center tween"
          :class="{ 'rotate-90': isOpen }"
        >
          <div
            class="icon w-6 h-6 text--secondary"
            :class="icon"
          />
        </div>
      </div>
      <slot v-if="$slots.title" name="title" />
      <div v-else class="flex-1 flex items-center gap-4">
        <div class="font-bold text-balance">
          {{ title }}
        </div>
        <slot v-if="$slots.side" name="side" />
      </div>
      <div
        v-if="iconRight"
        class="flex items-center"
      >
        <div
          class="w-8 h-8 mr-1 rounded-full hover:bg--secondary/20 flex items-center justify-center tween"
          :class="{ 'rotate-90': isOpen }"
        >
          <div class="icon w-6 h-6 text--secondary" :class="[iconRight]" />
        </div>
      </div>
    </div>
    <div
      class="grid overflow-hidden tween"
      :class="{ 'grid-rows-1': isOpen, 'grid-rows-0': !isOpen }"
    >
      <div class="min-h-0" :class="{ 'border-t-1 border--content/12': showDivider && isOpen }">
        <slot v-if="$slots.content" name="content" />
        <div
          v-else
          class="max-w-100vw"
          :class="contentClass"
        >
          <slot />
        </div>
      </div>
    </div>
    <slot name="append" v-bind="{ toggle, isOpen }" />
  </div>
</template>
