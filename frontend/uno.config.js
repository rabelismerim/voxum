import {
  defineConfig,
  presetAttributify,
  presetTypography,
  presetUno,
  presetWebFonts,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss'
import presetIcons from '@unocss/preset-icons'

const repeatIt = (string, count) => Array(+count).fill().map(() => string).join('')
function variant(start, selector) {
  return (matcher) => {
    const isString = typeof start === 'string'
    const begin = isString ? start : matcher.match(start)?.[0]
    if (!begin || !matcher.startsWith(begin))
      return matcher
    return {
      matcher: matcher.slice(begin?.length),
      selector: isString ? selector : selector(matcher.match(start)),
    }
  }
}

export default defineConfig({
  content: {
    pipeline: {
      include: [
        /\.(vue|svelte|[jt]sx|mdx?|astro|elm|php|phtml|html)($|\?)/,
        'src/**/*.{js,json}',
      ],
    },
  },
  rules: [
    ['block', { display: 'block !important' }],
    ['text-balance', { 'text-wrap': 'balance' }],
    [/^bg--([\w-]+)$/, ([, w]) => ({ background: `hsl(var(--${w},0,0%,0%))` })],
    [/^bg--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ background: `hsla(var(--${w},0,0%,0%),${+d / 100})` })],
    [/^text--([\w-]+)$/, ([, w]) => ({ color: `hsl(var(--${w},0,0%,0%))` })],
    [/^text--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ color: `hsl(var(--${w},0,0%,0%),${+d / 100})` })],
    [/^color--([\w-]+)$/, ([, w]) => ({ color: `hsl(var(--${w},0,0%,0%))` })],
    [/^color--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ color: `hsl(var(--${w},0,0%,0%),${+d / 100})` })],
    [/^fill--([\w-]+)$/, ([, w]) => ({ fill: `hsl(var(--${w},0,0%,0%))` })],
    [/^fill--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ fill: `hsla(var(--${w},0,0%,0%),${+d / 100})` })],
    [/^stop--([\w-]+)$/, ([, w]) => ({ 'stop-color': `hsl(var(--${w},0,0%,0%))` })],
    [/^stop--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ 'stop-color': `hsla(var(--${w},0,0%,0%),${+d / 100})` })],
    [/^stroke--([\w-]+)$/, ([, w]) => ({ stroke: `hsl(var(--${w},0,0%,0%))` })],
    [/^border--([\w-]+)$/, ([, w]) => ({ 'border-color': `hsl(var(--${w},0,0%,0%))` })],
    [/^border--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ 'border-color': `hsla(var(--${w},0,0%,0%),${+d / 100})` })],
    [/^outline--([\w-]+)$/, ([, w]) => ({ 'outline-color': `hsl(var(--${w},0,0%,0%))` })],
    [/^outline--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ 'outline-color': `hsla(var(--${w},0,0%,0%),${+d / 100})` })],
    ['max-w-fill', { 'max-width': '-webkit-fill-available' }],
    [/^ring--(\w+)$/, ([, w]) => ({ '--un-ring-color': `hsl(var(--${w},0,0%,0%))`, '--un-ring-offset-color': `hsl(var(--${w},0,0%,0%))` })],
    [/^ring--([\w-]+)\/(\d+)$/, ([, w, d]) => ({ '--un-ring-color': `hsla(var(--${w},0,0%,0%),${+d / 100})`, '--un-ring-offset-color': `hsla(var(--${w},0,0%,0%),${+d / 100})` })],
    ['ring-inner', { 'box-shadow': 'inset var(--un-ring-offset-shadow),inset var(--un-ring-shadow), var(--un-shadow) !important' }],
    ['text-vertical', { 'writing-mode': 'vertical-lr' }],
    ['grid-rows-0', { 'grid-template-rows': '0fr' }],
    ['grid-rows-1', { 'grid-template-rows': '1fr' }],
    ['grid-cols-0', { 'grid-template-columns': '0fr' }],
    ['grid-cols-1', { 'grid-template-columns': '1fr' }],
    [/^tween(-(\d+))*$/, ([,, d = 300]) => ({
      'transition-property': 'color,width,height,background-color,border-color,outline-color,text-decoration-color,fill,stroke,opacity,box-shadow,transform,filter,backdrop-filter,grid-template-rows,grid-template-columns,margin,padding,border-radius',
      'transition-timing-function': 'cubic-bezier(0.4, 0, 0.2, 1)',
      'transition-duration': `${d}ms`,
    })],
  ],
  variants: [
    variant('p-l-chkd:', s => `*:checked+* ${s}`),
    variant('l-chkd:', s => `*:checked+${s}`),
    variant(/^p-l-(\d+)th-chkd\:/, ([,d]) =>
      s => `*:checked+* ${repeatIt('*+', d)}${s}`),
    variant(/^l-(\d+)th-chkd\:/, ([,d]) =>
      s => `*:checked+${repeatIt('*+', d)}${s}`),
  ],
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      warn: true,
    }),
    presetTypography(),
    presetWebFonts({
      fonts: {
        sans: 'DM Sans',
        serif: 'DM Serif Display',
        mono: 'DM Mono',
      },
    }),
  ],
  transformers: [
    transformerDirectives(),
    transformerVariantGroup(),
  ],
})
