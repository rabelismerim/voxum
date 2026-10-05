export function print(message, ...error) {
  if (import.meta.env.VITE_LOG || import.meta.env.DEV)
    console.warn(message, ...error)
}

export const typeOf = obj => Object.prototype.toString.call(obj).slice(8, -1)

export const toCamel = (str = '') =>
  str.replace(/([-_][a-z])/ig, ($1) => $1.toUpperCase().replace('-', '').replace('_', ''))

export const toSnake = (str = '') =>
  str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)

export function set(path, obj, value) {
  const keys = path.split('.')
  let current = obj
  for (let i = 0; i < keys.length - 1; i++) {
    if (!current[keys[i]]) current[keys[i]] = {}
    current = current[keys[i]]
  }
  current[keys[keys.length - 1]] = value
}

export const toUpperCase = (text = '') => text.toUpperCase()

export function setValues(obj = {}, toApply, weak) {
  Object
    .entries(toApply)
    .map(([key, value]) => obj[key] = weak ? obj[key] ?? value : value)
  return obj
}

export const copyClipboard = (text) => navigator.clipboard.writeText(text)

export function useFormatDate(locale = 'pt-BR') {
  const _ = undefined
  const toUpperCaseStr = 'toUpperCase'
  const toLowerCaseStr = 'toLowerCase'
  const month = 'month'
  const weekday = 'weekday'
  const hours = 'getHours'
  const toStr = (value, length = 0) => (`${value}`).padStart(length, '0')
  const getDay = pad => date => toStr(date.getDate(), pad)
  const getMonth = pad => date => toStr(date.getMonth() + 1, pad)
  const getYear = pad => date => toStr(date.getFullYear()).slice(pad)
  const getHours = pad => date => toStr(date[hours](), pad)
  const getHalfHours = pad => date => toStr(date[hours]() - (date[hours]() >= 12 ? 12 : 0), pad)
  const getMinutes = pad => date => toStr(date.getMinutes(), pad)
  const getSeconds = pad => date => toStr(date.getSeconds(), pad)
  const getHalfDay = isUpperCase => (date) => {
    date = toStr(date[hours]() >= 12 ? 'pm' : 'am')
    return isUpperCase ? date[toUpperCaseStr]() : date
  }
  const getDateName = (name, modifier, isShort) => (date) => {
    date = date.toLocaleDateString(locale, { [name]: isShort ? 'short' : 'long' })
    date = date[0][toUpperCaseStr]() + date.slice(1)
    return modifier ? date[modifier]() : date
  }
  const formatters = {
    DDDD: getDateName(weekday, toUpperCaseStr),
    dddd: getDateName(weekday, toLowerCaseStr),
    Dddd: getDateName(weekday),
    DDD: getDateName(weekday, toUpperCaseStr, true),
    ddd: getDateName(weekday, toLowerCaseStr, true),
    Ddd: getDateName(weekday, _, true),
    DD: getDay(2),
    D: getDay(),
    MMMM: getDateName(month, toUpperCaseStr),
    mmmm: getDateName(month, toLowerCaseStr),
    Mmmm: getDateName(month),
    MMM: getDateName(month, toUpperCaseStr, true),
    mmm: getDateName(month, toLowerCaseStr, true),
    Mmm: getDateName(month, _, true),
    MM: getMonth(2),
    M: getMonth(),
    YYYY: getYear(),
    YY: getYear(-2),
    HH: getHours(2),
    H: getHours(),
    hh: getHalfHours(2),
    h: getHalfHours(),
    mm: getMinutes(2),
    m: getMinutes(),
    ss: getSeconds(2),
    s: getSeconds(),
    a: getHalfDay(),
    A: getHalfDay(true),
  }
  return (date, str = '@DD/@MM/@YYYY', fallback = '') => !date
    ? fallback
    : str?.replace(/(@[ADHMYadhms]+)/g, (match) => {
      date = typeof date === 'string' ? new Date(date) : date
      if (!date)
        return fallback
      const formatter = formatters[match.slice(1)]
      return formatter ? formatter(date) : match
    })
}

export const formatDate = useFormatDate()

export function formatDateToBackend(value) {
  if (!value)
    return
  const [day, month, year] = value.split('/')
  return `${year}-${month}-${day}`
}

export const formatMoney = (value, currency = 'BRL') => Intl.NumberFormat('pt-BR', { style: 'currency', currency }).format(value || 0)

export function formatLegalNumber(value) {
  if (!value)
    return
  value = value?.padStart(11, '0')?.replace(/[./-]/gi, '')
  if (value.length < 14) {
    const [, first, second, third, digit] = value
      .padEnd(11, '0')
      .split(/^(\d{3})(\d{3})(\d{3})(\d{2})/)
    return `${first}.${second}.${third}-${digit}`
  }

  const [, first, second, third, fourth, digit] = value
    .padEnd(14, '0')
    .split(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/)
  return `${first}.${second}.${third}/${fourth}-${digit}`
}

export function getInitials(text = '') {
  const initials = text
    .toUpperCase()
    .split(' ')
    .map(word => word[0])
    .join('')
  if (initials.length < 2)
    return text.toUpperCase().slice(0, 2)
  if (initials.length > 2)
    return initials.slice(0, 2)
  return initials
}

export const redirectTo = url => window.location.replace(url)

export const isType = (obj, ...types) => types.includes(typeOf(obj))

export const clone = obj => {
  if (!obj || isType(obj, 'Undefined', 'Null', 'String', 'Number', 'Boolean'))
    return obj
  if (isType(obj, 'Array'))
    return obj.map(child => clone(child))
  if (!isType(obj, 'Object')) return obj
  if (obj?.nodeType && isType(obj?.cloneNode, 'Function'))
    return obj.cloneNode(true)
  if (isType(obj, 'Date'))
    return new Date(obj)
  if (isType(obj, 'RegExp'))
    return new RegExp(obj)
  const newObj = {}
  for (const key in obj)
    newObj[key] = clone(obj[key])
  return newObj
}

export function swapElements(array, index1, index2 = index1 + 1) {
  [array[index1], array[index2]] = [array[index2], array[index1]]
}

export function swap(list, index1, index2 = index1 + 1) {
  const array = clone(list)
  const temp = array[index1]
  array[index1] = array[index2]
  array[index2] = temp
  return array
}

export function delay(seconds) {
  return new Promise(resolve =>
    setTimeout(() => resolve(true), seconds * 1000))
}

function sum(array, start) {
  return array.reduce((total, el, i) => total + el * (start - i), 0)
}

const rest = value => value % 11
const format = value => value.replace(/[^\d]+/g, '')

function isValidNumber(value, count) {
  return format(value).length === count && !format(value).match(/(\d)\1{10}/)
}

function validator(value) {
  return format(value)
    .split('')
    .splice(format(value).length - 2)
    .map(el => +el)
}

function validate(firstDigit, lastDigit, validatorArr) {
  return firstDigit === validatorArr[0] && lastDigit === validatorArr[1]
}

function toValidate(value, end, start = 0) {
  return format(value)
    .split('')
    .filter((digit, index) => index >= start && index <= end && digit)
    .map(el => +el)
}

export function isValidCPF(cpf) {
  if (!isValidNumber(cpf, 11))
    return false
  const digit = (end, factor) =>
    rest(sum(toValidate(cpf, end), factor) * 10) % 10
  const firstDigit = digit(8, 10)
  const lastDigit = digit(9, 11)
  return validate(firstDigit, lastDigit, validator(cpf))
}

export function isValidCNPJ(cnpj) {
  if (!isValidNumber(cnpj, 14))
    return false
  const digit = sumValue => rest(sumValue) < 2 ? 0 : 11 - rest(sumValue)
  const firstDigit = digit(sum(toValidate(cnpj, 3), 5) + sum(toValidate(cnpj, 11, 4), 9))
  const lastDigit = digit(sum(toValidate(cnpj, 4), 6) + sum(toValidate(cnpj, 12, 5), 9))
  return validate(firstDigit, lastDigit, validator(cnpj))
}

export function rangeBetween(start = 0, end = 0, count = 1) {
  return Array(count < 0 ? 0 : count).fill(0)
    .map((_, i) => start + ((end - start) / (count <= 1 ? 1 : count - 1) * i))
}

export function flatten(data, options = { array: false }) {
  const result = {}
  function recurse(cur, prop) {
    if (Object(cur) !== cur) {
      result[prop] = cur
    }
    else if (Array.isArray(cur)) {
      const l = cur.length
      for (let i = 0; i < l; i++)
        recurse(cur[i], `${prop}[${i}]`)
      if (l === 0)
        result[prop] = []
      if (options.array)
        result[prop] = cur
    }
    else {
      let isEmpty = true
      for (const p in cur) {
        isEmpty = false
        recurse(cur[p], prop ? `${prop}.${p}` : p)
      }
      if (isEmpty && prop)
        result[prop] = {}
    }
  }
  recurse(data, '')
  return result
}

export function unflatten(data) {
  if (Object(data) !== data || Array.isArray(data))
    return data
  const regex = /\.?([^.\[\]]+)|\[(\d+)\]/g
  const resultholder = {}
  for (const p in data) {
    let cur = resultholder
    let prop = ''
    let m = regex.exec(p)
    while (m) {
      cur = cur[prop] || (cur[prop] = (m[2] ? [] : {}))
      prop = m[2] || m[1]
      m = regex.exec(p)
    }
    cur[prop] = data[p]
  }
  return resultholder[''] || resultholder
}

export function parseToCamel(data) {
  return unflatten(Object
    .fromEntries(Object.entries(flatten(data))
      .map(([key, value]) => {
        const regex = /(\[\d+\]|\.)/
        return [
          key.split(regex)
            .map(item => item.match(regex) ? item : toCamel(item))
            .join(''),
          value,
        ]
      }),
    ))
}

export function parseToSnake(data) {
  return unflatten(Object
    .fromEntries(Object.entries(flatten(data))
      .map(([key, value]) => {
        const regex = /(\[\d+\]|\.)/
        return [
          key.split(regex)
            .map(item => item.match(regex) ? item : toSnake(item))
            .join(''),
          value,
        ]
      }),
    ))
}

export function saveFile(data, fileName = 'download', fileExtension = 'txt') {
  const getType = () => {
    if (['jpg', 'jpeg'].includes(fileExtension))
      return 'image/jpeg'
    if (['png', 'apng'].includes(fileExtension))
      return 'image/png'
    if (['gif'].includes(fileExtension))
      return 'image/gif'
    if (['pdf'].includes(fileExtension))
      return 'application/pdf'
    if (['xlsx'].includes(fileExtension))
      return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    if (['html'].includes(fileExtension))
      return 'text/html'
    return 'text/plain'
  }

  const blob = (() => {
    if (data instanceof Blob)
      return data
    if (fileExtension === 'csv')
      return new Blob([new Uint8Array([239, 187, 191]), 'Text', data], { type: 'text/plain;charset=utf-8' })
    if (['pdf', 'xlsx'].includes(fileExtension)) {
      const byteCharacters = atob(data)
      const byteNumbers = byteCharacters
        .split('')
        .map((_, index) => byteCharacters.charCodeAt(index))
      const byteArray = new Uint8Array(byteNumbers)
      return new Blob([byteArray], { type: getType() })
    }
    return new Blob([data], { type: getType() })
  })()

  const link = document.createElement('a')
  const url = window.webkitURL != null
    ? window.webkitURL.createObjectURL(blob)
    : window.URL.createObjectURL(blob)

  document.body.appendChild(link)
  link.style.display = 'none'
  link.href = url
  link.download = `${fileName}.${fileExtension}`
  link.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(link)
}

export function getCanvasFile(canvas, name = 'file', type = 'png') {
  if (!canvas)
    return
  const imageType = `image/${type}`
  const [, dataURL] = canvas.toDataURL(imageType).split(',')
  const blobBin = atob(dataURL)
  const array = []
  for (const i in blobBin)
    array.push(blobBin.charCodeAt(i))
  return new File([new Uint8Array(array)], `${name}.${type}`, { type: imageType })
}

export const controlPagination = (pagination = {}, extraPagination = {}) => {
  const {
    rowsPerPage = 10,
    page = 1,
    sortBy,
    descending,
    filterBy,
    filterColumn
  } = pagination
  const usePagination = {
    limit: rowsPerPage,
    offset: rowsPerPage * (page - 1),
    ordering: sortBy && `${descending ? '-' : ''}${sortBy}`,
    [filterColumn ?? '']: filterBy,
    ...extraPagination,
  }
  return `?${Object.entries(usePagination)
    .filter(([key, value]) => key && value)
    .flatMap(([key, value]) => Array.isArray(value) ? value.map(item => [key, item]) : [[key, value]])
    .map(([key, value]) => `${key}=${value}`).join('&')}`
}

const fnMap = new Map()
export const debounce = (data, ...args) => {
  const [func, timeout = 500] = Array.isArray(data) ? data : [data]
  let timeoutId = fnMap.get(func)
  if (timeoutId) clearTimeout(timeoutId)
  timeoutId = setTimeout(() => {
    func(...args)
    fnMap.delete(func)
  }, timeout)
  fnMap.set(func, timeoutId)
}

export const isSame = (obj1, obj2) => {
  const getType = (obj, type = typeof obj) =>
    (type === 'number' && isNaN(obj))
      ? 'NaN'
      : (type === 'object' && obj === null)
        ? 'null'
        : (type === 'object' && Array.isArray(obj))
          ? 'array'
          : type

  const type1 = getType(obj1)
  const type2 = getType(obj2)
  if (type1 !== type2) return false
  const type = type1
  if (obj1 === obj2 || type === 'NaN') return true
  if (type === 'string' || type === 'number') return obj1 === obj2
  if (type === 'array') {
    if (obj1.length !== obj2.length) return false
    for (let i = 0; i < obj1.length; i++) {
      const result = isSame(obj1[i], obj2[i])
      if (!result) return false
    }
    return true
  }
  if (type === 'object') {
    const keys1 = Object.keys(obj1)
    const keys2 = Object.keys(obj2)
    if (keys1.length !== keys2.length) return false
    for (let i = 0; i < keys1.length; i++) {
      const key = keys1[i]
      const result = isSame(obj1[key], obj2[key])
      if (!result) return false
    }
    return true
  }
  return false
}