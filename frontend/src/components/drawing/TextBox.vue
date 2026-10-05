<script setup>
const props = defineProps({
  modelValue: {
    type: String,
  },
  x: {
    type: [Number, String],
    default: 0,
  },
  y: {
    type: [Number, String],
    default: 0,
  },
  width: {
    type: [Number, String],
  },
  height: {
    type: [Number, String],
  },
  lines: {
    type: [Number, String],
  },
  padding: {
    type: [String, Number, Array],
    default: 0,
  },
  align: {
    type: String,
    default: 'left', // 'left' || 'center' || 'right'
  },
  radius: {
    type: [Number, String],
    default: 0,
  },
  background: {
    type: String,
  },
  backgroundOpacity: {
    type: [Number, String],
    default: 1,
  },
  border: {
    type: String,
    default: '#000',
  },
  borderWidth: {
    type: [Number, String],
    default: 0,
  },
  borderOpacity: {
    type: [Number, String],
    default: 1,
  },
  color: {
    type: String,
    default: '#000',
  },
  afterBreak: {
    type: [Number, String],
    default: 0,
  },
  ellipsis: {
    type: Boolean,
    default: true,
  },
  fontFamily: {
    type: String,
    default: 'Arial, sans-serif',
  },
  fontSize: {
    type: [String, Number],
    default: 16,
  },
  lineHeight: {
    type: [String, Number],
    default: 1,
  },
  bold: {
    type: Boolean,
  },
})

const inlineStyle = $computed(() => ({
  fontFamily: props.fontFamily,
  fontSize: `${props.fontSize}px`,
}))

function createEl(selector, isText) {
  return document[`create${isText ? 'TextNode' : 'Element'}`](selector)
}

function createSVG(selector) {
  return document.createElementNS('http://www.w3.org/2000/svg', selector)
}

function insert(shouldAppend, parent, ...children) {
  return children.map(child =>
    parent[`${shouldAppend ? 'append' : 'remove'}Child`](child),
  )
}

function setStyle(element, style) {
  for (const key in style)
    element.style[key] = style[key]
}

function getSize(content) {
  if (typeof document === 'undefined')
    return { width: 0, height: 0 }
  const data = createEl(content, true)
  const svg = createSVG('svg')
  const text = createSVG('text')
  setStyle(text, inlineStyle)
  insert(true, text, data)
  insert(true, svg, text)
  insert(true, document.body, svg)
  const { width, height } = text.getBBox()
  insert(false, svg, text)
  insert(false, document.body, svg)
  return { width, height }
}

const baselineHeight = $computed(() => {
  if (typeof document === 'undefined')
    return 0
  const container = createEl('div')
  const span = createEl('span')
  const baselineLocator = createEl('img')
  setStyle(container, inlineStyle)
  setStyle(baselineLocator, { verticalAlign: 'baseline' })
  insert(true, document.body, container)
  insert(true, container, span, baselineLocator)
  const { bottom: bottomY } = span.getBoundingClientRect()
  const { bottom: baselineY } = baselineLocator.getBoundingClientRect()
  insert(false, container, span, baselineLocator)
  insert(false, document.body, container)
  return bottomY - baselineY
})

const localPadding = $computed(() => {
  let padding = props.padding
  if (typeof padding === 'string')
    padding = padding.split(' ').map(e => +e)
  if (typeof padding === 'number')
    padding = [padding]
  if (padding?.length === 1)
    return Array(4).fill(padding[0])
  if (padding?.length === 2)
    return [padding[0], padding[1], padding[0], padding[1]]
  return padding ?? [0, 0, 0, 0]
})

const horizontalPadding = $computed(() => localPadding[1] + localPadding[3])
const verticalPadding = $computed(() => localPadding[0] + localPadding[2])
const textSize = $computed(() => getSize(props.modelValue ?? ''))

const innerSize = $computed(() => ({
  width: (props.width ? +props.width : 0) - horizontalPadding,
  height: (props.height ? +props.height : 0) - verticalPadding,
}))

const lines = $computed(() => {
  const content = props.modelValue ?? ''
  const length = content?.length ?? 0
  const innerWidth = innerSize.width
  const computedLines = []
  let start = 0
  let lineBreaks = 0

  for (let i = 0; i <= length; i++) {
    const { width } = getSize(content.slice(start, i))
    const isBreak = content[i] === '\n' || i === length
    const endPos = isBreak ? i + 1 : i - 1
    if ((innerWidth > 0 && width >= innerWidth) || isBreak) {
      computedLines.push([content.slice(start, endPos).trim(), lineBreaks, width])
      start = endPos
    }
    if (isBreak)
      lineBreaks++
  }

  const useLines = computedLines
    .map(([line, breaksCount, width], i) => [
      line,
      props.fontSize
        - baselineHeight
        + i * (textSize.height - baselineHeight) * props.lineHeight
        + breaksCount * +props.afterBreak,
      width,
    ])
    .filter(([, posY], i) => {
      if (props.lines)
        return i < props.lines
      if (innerSize.height > 0)
        return posY < innerSize.height
      return true
    })

  const lastLine = useLines.at(-1)?.[0]
  if (
    props.ellipsis
    && lastLine
    && (+props.height > 0 || props.lines > 0)
    && innerWidth > 0
    && getSize(`${lastLine}...`).width > innerWidth
  ) {
    useLines.at(-1)[0] = `${lastLine.slice(0, -2)}...`
  }

  return useLines
})

const maxLineWidth = $computed(
  () => lines.reduce((acc, [, , width]) => (width > acc ? width : acc), 0),
)

const realWidth = $computed(
  () => (props.width !== undefined ? +props.width : maxLineWidth + horizontalPadding),
)

const realHeight = $computed(() =>
  !props.height || props.lines
    ? (lines.at(-1)?.[1] ?? 0) + verticalPadding
    : +props.height,
)
</script>

<template>
  <g
    :transform="`translate(${x},${y})`"
    :style="{ fontFamily, fontSize: `${fontSize}px` }"
  >
    <rect
      v-if="background"
      x="0"
      y="0"
      :width="realWidth"
      :height="realHeight"
      :rx="radius"
      :fill="background"
      :fill-opacity="backgroundOpacity"
      :stroke="border"
      :stroke-width="borderWidth"
      :stroke-opacity="borderOpacity"
    />
    <text
      v-for="([line, posY], i) in lines"
      :key="i"
      :fill="color"
      :font-weight="bold ? 'bold' : undefined"
      :x="
        (align === 'left'
          ? 0
          : align === 'right'
            ? innerSize.width
            : innerSize.width / 2) + localPadding[3]
      "
      :y="posY + localPadding[0]"
      :text-anchor="
        align === 'left' ? 'start' : align === 'right' ? 'end' : 'middle'
      "
    >
      {{ line }}
    </text>
  </g>
</template>