<script setup>
const props = defineProps({
  icon: {
    type: String,
  },
  loading: {
    type: Boolean,
  },
  color: {
    type: String,
    default: 'secondary',
  },
  transparent: {
    type: Boolean,
  },
  tooltip: {
    type: String,
  },
  disabled: {
    type: Boolean,
  },
  outlined: {
    type: Boolean,
  },
  rounded: {
    type: Boolean,
  },
  filled: {
    type: Boolean,
  },
})
const emit = defineEmits(['click', 'press'])
const {isMobile} = useAmbient()
</script>

<template>
  <button
    :disabled="disabled ? disabled : undefined"
    class="relative group overflow-hidden text-xl h-9 w-9 justify-center items-center flex tween"
    :class="{
      'text--color rounded-1': transparent,
      'bg--base text--color rounded-1': !transparent,
      'border-1 border--content/12': outlined,
      'rounded-full': rounded,
      'opacity-100': disabled,
      'bg--color! color-white!': filled,
    }"
    :style="{
      '--color': `var(--${color})`,
    }"
    tabindex="0"
    @keyup.space="emit('press')"
    @click="emit('click', $event)"
  >
    <Spinner
      v-if="loading"
      :color="!transparent && !outlined ? 'white' : color"
      class="pointer-events-none tween"
      :class="loading ? 'opacity-100 scale-100' : 'opacity-0 scale-0'"
    />
    <div v-else>
      <div :class="icon" class="pointer-events-none" />
    </div>
    <slot v-if="$slots.default"/>
    <div
      v-if="!disabled"
      class="bg--color opacity-0 group-hover:opacity-15 inset-0 absolute tween"
    />
    <QTooltip v-if="tooltip && !isMobile()">
      {{ tooltip }}
    </QTooltip>
  </button>
</template>
