<script setup>
const props = defineProps({
  label: {
    type: String,
    default: 'Clique aqui',
  },
  loadingLabel: {
    type: String,
    default: 'Carregando...',
  },
  icon: {
    type: String,
  },
  align: {
    type: String,
    default: 'center',
  },
  loading: {
    type: Boolean,
  },
  color: {
    type: String,
    default: 'primary',
  },
  transparent: {
    type: Boolean,
  },
  tooltip: {
    type: String,
  },
  grow: {
    type: Boolean,
  },
  disabled: {
    type: Boolean,
  },
  outlined: {
    type: Boolean,
  },
  tag: {
    type: String,
    default: 'button',
  },
})
const emit = defineEmits(['click', 'press'])
const {isMobile} = useAmbient()
const target = ref(null)

defineExpose({ target })
</script>

<template>
  <component
    ref="target"
    :is="tag"
    :disabled="disabled ? disabled : undefined"
    class="group relative overflow-hidden min-h-9 font-semibold leading-1rem px-4 py-1.5 flex gap-.5em no-wrap items-center tween cursor-pointer"
    :class="{
      'text--color border-1 border--color rounded-1': outlined,
      'hover:bg--color/10 text--color rounded-1': transparent,
      'bg--color text-white border-1 border--content/12 rounded-1': !transparent && !outlined,
      'h-full rounded-0 min-w-fit': grow,
      'active:scale-110': !grow && !disabled && !transparent,
    }"
    :style="{
      'justify-content': align,
      '--color': `var(--${color})`,
    }"
    tabindex="0"
    @keyup.space="emit('press')"
    @click="emit('click', $event)"
  >
    <div v-show="loading" class="flex items-center nowrap gap-4 pointer-events-none whitespace-nowrap">
      {{ loadingLabel }}
      <Spinner
        :color="!transparent && !outlined ? 'white' : color"
        class="pointer-events-none tween"
        :class="loading ? 'opacity-100 scale-100' : 'opacity-0 scale-0'"
      />
    </div>
    <div v-show="!loading" class="pointer-events-none flex items-center gap-2 no-wrap">
      <slot name="before" />
      <slot v-if="$slots.label" name="label" />
      <span v-else class="whitespace-nowrap">{{ label }}</span>
      <slot name="after" />
    </div>
    <div v-show="icon" :class="icon" class="tween pointer-events-none" />
    <slot v-if="$slots.default" />
    <div
      class="opacity-0 group-hover:opacity-15 inset-0 absolute tween"
      :class="{
        'mix-blend-color-burn bg-gray-6': !transparent && !outlined,
        'mix-blend-screen bg-current-color': transparent,
        'bg-current-color': outlined,
      }"
    />
    <QTooltip v-if="tooltip && !isMobile()">
      {{ tooltip }}
    </QTooltip>
  </component>
</template>
