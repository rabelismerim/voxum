<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
  },
  title: {
    type: String,
  },
  subtitle: {
    type: String,
  },
  tooltip: {
    type: String,
  },
  modalClass: {
    type: String,
    default: '',
  },
  hideTitle: {
    type: Boolean,
  },
  hideClose: {
    type: Boolean,
  },
  notStack: {
    type: Boolean,
  },
  closeDisable: {
    type: Boolean,
  },
  loading: {
    type: Boolean,
  },
  exitConfirmation: {
    type: String,
  },
  canFullscreen: {
    type: Boolean,
  },
})
const emit = defineEmits(['update:model-value', 'close'])

const { dialog } = useQuasar()

const isFullscreen = ref(false)
let isOpen = $ref(false)
function update() {
  emit('update:model-value', isOpen)
}
watch(() => props.modelValue, open => {
  isOpen = open
  if(!isOpen) isFullscreen.value = false
})

function toggle() {
  isOpen = !isOpen
}

function exit() {
  isOpen = false
  update()
  emit('close')
}
function close() {
  if(!props.exitConfirmation) {
    exit()
    return
  }
  dialog({
    title: 'Confirmação de saída',
    message: props.exitConfirmation,
    ok: true,
    cancel: true,
  }).onOk(() => exit())
}

defineExpose({
  isFullscreen
})
</script>

<template>
  <div v-if="$slots.button">
    <slot name="button" v-bind="{ toggle, isOpen }" />
  </div>
  <Teleport to="body">
    <div
      class="fixed inset-0 flex bg-black/30 dark:bg-black/50 z-1000 tween"
      :class="{
        'opacity-100 pointer-events-auto': isOpen,
        'opacity-0 pointer-events-none': !isOpen,
        'justify-center items-end lg:items-center': !notStack,
        'justify-center items-center': notStack,
      }"
    >
      <div
        class="relative bg--base w-full m-0 lg:m-4 max-h-[calc(100vh-32px)] rounded-1 border-1 border-black/28 tween"
        :class="{
          'translate-y-10': !isOpen,
          'max-w-240': !modalClass,
          [modalClass]: modalClass,
          'w-full! h-full! max-w-unset! max-h-unset! m-0!': isFullscreen,
        }"
      >
        <button
          v-if="!hideClose"
          :disabled="closeDisable"
          class="absolute h-8 w-8 flex justify-center items-center text-lg rounded-full bg-black/6 hover:bg-black/12 tween z-100"
          :class="{
            'top-2 right-2': hideTitle,
            'top-4 right-4': !hideTitle
          }"
          @click="close"
        >
          <div class="i-carbon-close" />
          <QTooltip>{{ closeDisable ? 'Ação não permitida' : 'Fechar' }}</QTooltip>
        </button>
        <div
          v-if="!hideTitle"
          class="flex gap-2 relative p-4 sm:pb-5"
        >
        <div class="flex-1 flex items-center gap-3">
          <BtnIcon
            v-if="canFullscreen"
            icon="i-carbon-fit-to-screen"
            class="rounded-1"
            color="primary"
            tooltip="Tela cheia"
            @click="isFullscreen = !isFullscreen"
          />
            <div>
              <div>
                <span class="font-bold text-2xl">{{ title }}
                  <Hint :value="tooltip" class="ml-2" />
                </span>
              </div>
              <div v-if="subtitle" class="font-bold opacity-70">
                {{ subtitle }}
              </div>
            </div>
            <slot name="side" />
          </div>
          <QLinearProgress
            v-if="loading"
            indeterminate
            color="secondary"
            class="absolute bottom-0 left-0"
            size="xs"
          />
        </div>
        <slot />
      </div>
    </div>
  </Teleport>
</template>
