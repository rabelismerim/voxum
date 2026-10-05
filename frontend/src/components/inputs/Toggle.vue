<script setup>
defineProps({
  label: {
    type: String,
    default: '',
  },
  sliderClass: {
    type: String,
    default: 'bg--secondary',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const checked = defineModel({ default: false, type: Boolean })
</script>

<template>
  <label class="group flex items-center gap-2 cursor-pointer">
    <div
      v-if="label"
      :class="{
        'opacity-50!': disabled,
      }"
    >
      {{ label }}
    </div>
    <div class="relative inline-block w-8.5 h-5">
      <input
        :checked="checked"
        type="checkbox"
        class="toggle opacity-0 w-0 h-0"
        :disabled="disabled"
        @change="checked = !checked"
      >
      <span
        class="slider absolute cursor-pointer inset-0 rounded-4.25 border-1 border--content/12 transition-all duration-400"
        :class="{
          [sliderClass]: checked,
          'before:translate-x-0.875rem': checked,
          'bg--content/20': !checked,
          'bg--content/10! cursor-not-allowed': disabled,
        }"
      />
    </div>
  </label>
</template>

<style lang="scss" scoped>
.slider:before {
  position: absolute;
  content: "";
  height: 0.875rem;
  width: 0.875rem;
  left: 0.135rem;
  top: 0.125rem;
  background-color: white;
  transition: all 0.4s !important;
  border-radius: 50%;
}
.toggle:focus-visible + .slider {
  box-shadow: 0 0 0 2px hsl(var(--primary));
}
</style>