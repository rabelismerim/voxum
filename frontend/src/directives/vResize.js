function debounce(func, delay) {
  let timer
  return function (...args) {
    clearTimeout(timer)
    timer = setTimeout(() => func(...args), delay)
  }
}

class Resizer {
  resizeObserver = null
  element = null
  width = 0
  height = 0
  options = {}

  constructor(el, options) {
    let $el = el
    if (typeof el === 'string') {
      $el = document.querySelector(el)
    }

    this.element = $el
    this.options = Object.assign({
      delay: 150,
    }, options)

    this.observe(this.element)
  }

  observe(element) {
    if (element) {
      this.element = element
    } else {
      element = this.element
    }

    if (!(element instanceof HTMLElement)) {
      throw new Error('The target element must be a HTMLElement')
    }

    const { width, height } = element.getBoundingClientRect()
    this.width = Math.floor(width)
    this.height = Math.floor(height)

    if (this.resizeObserver) {
      this.disconnect()
    }

    this.resizeObserver = new ResizeObserver(this._onResize())
    this.resizeObserver.observe(element)
  }

  _onResize() {
    const delay = this.options.delay || this.options.wait
    if (delay) {
      return debounce(this._handleResize.bind(this), delay)
    }

    return this._handleResize.bind(this)
  }

  _handleResize(entries) {
    for (const entry of entries) {
      const target = entry.target
      let { width, height } = target.getBoundingClientRect()
      width = Math.floor(width)
      height = Math.floor(height)

      if (this.width !== width || this.height !== height) {
        this.width = width
        this.height = height

        if (typeof this.options.resize === 'function') {
          this.options.resize({ width, height }, target)
        }
      }
    }
  }

  disconnect() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect()
      this.resizeObserver = null
    }
  }

  destroy() {
    this.disconnect()
    this.element = null
  }
}

function getOptions({ value, arg }) {
  const options = {}
  if (typeof value === 'function') {
    options.resize = value
  }

  const parsedArg = Number.parseInt(arg)
  options.delay = Number.isNaN(parsedArg) ? 50 : parsedArg

  return options
}

const vResize = {
  mounted(el, binding) {
    const { value } = binding
    if (value && typeof value !== 'function') {
      console.warn('v-resize should receive a function as value')
      return
    }

    if (!(el && typeof el.getBoundingClientRect === 'function')) {
      throw new Error('The target element must be a HTMLElement')
    }

    const { width, height } = el.getBoundingClientRect()
    if (typeof value === 'function') {
      value({
        width: Math.floor(width),
        height: Math.floor(height),
      }, el)
    }

    const ro = new Resizer(el, getOptions(binding))
    el.__vue_resize__ = ro
  },
  beforeUnmount(el) {
    const ro = el.__vue_resize__
    if (ro) {
      ro.destroy()
      delete el.__vue_resize__
    }
  },
}

export default vResize