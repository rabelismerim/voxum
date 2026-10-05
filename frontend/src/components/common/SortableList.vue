<script setup>
const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
})
const emit = defineEmits(['update:items'])

let localItems = $ref(clone(props.items))
watchEffect(() => {
  localItems = clone(props.items)
})
let dragging = $ref(-1)

function onDragStart(index) {
  dragging = index
}
function onDragEnter(evt, index) {
  const { target } = evt
  target.classList.add('over')
  const children = [...target.children]
  children.forEach(el => el.style.pointerEvents = 'none')
}
function onDragOver(evt) {
  //   const {
  //     y: posY,
  //     target
  //   } = evt
  //   const {
  //     y: targetY,
  //     height
  //   } = target.getBoundingClientRect()
}
function onDragLeave(evt, index) {
  const { target } = evt
  target.classList.remove('over')
  const children = [...target.children]
  children.forEach(el => el.style.pointerEvents = 'auto')
}
function onDrop(evt, index) {
  const { target } = evt
  target.classList.remove('over')
  const children = [...target.children]
  children.forEach((el) => {
    el.style.pointerEvents = 'auto'
  })
  if (dragging < 0)
    return
  const item = localItems[dragging]
  localItems.splice(dragging, 1)
  localItems.splice(index, 0, item)
  dragging = -1
  emit('update:items', clone(localItems))
}

function remove(index) {
  localItems.splice(index, 1)
  emit('update:items', clone(localItems))
}
</script>

<template>
  <ul v-auto-animate="{ duration: 500 }">
    <li
      v-for="(item, index) in localItems"
      :key="item"
      draggable="true"
      class="flex flex-nowrap items-center mb-4"
      @dragstart="onDragStart(index)"
      @dragenter.self="onDragEnter($event, index)"
      @dragleave.self="onDragLeave"
      @dragover.prevent="onDragOver"
      @drop.self="onDrop($event, index)"
    >
      <div class="py-2 px-.1 hover:bg--primary/30 hover:color--primary color-black/40 mr-1 rounded cursor-pointer">
        <div class="i-tabler-grip-vertical text-xl" />
      </div>
      <div class="flex-1">
        <slot v-bind="{ item, remove: () => remove(index) }" />
      </div>
    </li>
  </ul>
</template>
