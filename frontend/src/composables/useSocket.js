import { reactive, computed } from 'vue'
import useAmbient from './useambient'
import {
  print,
  clone,
  toCamel,
  typeOf,
  parseToCamel,
  flatten,
  set,
  debounce
} from './useUtils'

const { token: configuredToken, socketHost, socketPort } = useAmbient()

const maxConnectionAttempts = 12
const reconnectionDelay = 5000

const connectionAttempts = {}
const queue = {}
const nullData = {
  connected: false,
  status: 'UNSET',
  connectionAttempts: 0,
  channels: {},
}
const sockets = reactive({})

if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    for (const url in sockets)
      reconnect(url)
  })
  window.addEventListener('offline', () => {
    for (const url in sockets)
      close(url)
  })
}

function open(url) {
  const { protocol, hostname, port } = window.location
  const token = window.sessionStorage.getItem('APP_TOKEN') || configuredToken
  const useSocketHost = `${socketHost || `${protocol.replace('http', 'ws')}//${hostname}`}${!!(socketPort || port) ? `:${socketPort || port}` : ''}`
  const socketURL = `${useSocketHost}/voxum/ws/${url}/${token ? `?token=${encodeURI(token)}` : ''}`
  print('WEBSOCKET CONFIG:', { socketHost, socketPort, authenticated: Boolean(token), url })

  const socket = new WebSocket(socketURL, ['V2'])
  const data = sockets[url]?.data || reactive(clone(nullData))
  if (!connectionAttempts[url])
    connectionAttempts[url] = 0

  const onConnection = () => {
    data.status = 'CONNECTED'
    data.connected = true
    delete connectionAttempts[url]
    delete queue[url]
  }
  socket.onopen = () => {
    print(`WEBSOCKET: ${url}`, '\n >>> CONNECTED!')
    onConnection()
  }

  socket.onclose = (event) => {
    const { code, reason } = event
    print(`WEBSOCKET: ${url}`, '\n >>> CLOSED:\n', { code, reason, event })
    data.status = 'CLOSED'
    reconnect(url)
  }

  socket.onerror = (...error) => {
    print(`WEBSOCKET: ${url}`, '\n >>> ERROR:', ...error)
    data.status = 'ERROR'
  }

  socket.onmessage = async (event) => {
    onConnection()
    const { data: message } = event
    const { channel, data: newData, channel_type: channelType } = JSON.parse(message)
    const channelName = toCamel(channel)
    if (!newData) {
      print(`WEBSOCKET: ${url}`, `\n >>> CLEAR: ${channelName} {{${channelType}}}`, { channel, newData })
      data.channels[channelName] = undefined
      return
    }
    let channelData = data.channels[channelName]
    const dataBody = typeOf(newData) === 'String' ? JSON.parse(newData) : newData
    const useData = parseToCamel(dataBody)

    print(`WEBSOCKET: ${url}`, `\n >>> MESSAGE: ${channelName} {{${channelType}}}\n`, { channel, useData })

    if (channelType.includes('object') && channelType.includes('patch')) {
      const patch = flatten(useData)
      const patchData = data.channels[channelName]
      if (patchData)
        for (const key in patch)
          set(key, patchData, patch[key])
      else
        data.channels[channelName] = useData
      return
    }

    if (channelType.includes('array') && channelType.includes('patch')) {
      const patch = useData
      const patchData = data.channels[channelName]?.data ?? []
      const patchItem = Array.isArray(patchData) && patchData?.find(({ id }) => id === patch.id)
      if (patchItem) {
        for (const key in patch)
          patchItem[key] = patch[key]
      }
    }

    if (['patch', 'update', 'delete'].some(type => channelType.includes(type))) {
      data.channels[channelName] = {
        type: channelType.split('_')[1],
        data: useData,
      }
      debounce(() => data.channels[channelName] = undefined)
      return
    }

    if (channelType === 'object') {
      data.channels[channelName] = useData
      return
    }

    const isArray = ['array', 'list'].includes(channelType)
    if (isArray && !channelData?.data) {
      data.channels[channelName] = {
        pages: {},
        data: [],
        ids: [],
        total: 0,
        numOfPages: 0,
        loading: true,
      }
      channelData = data.channels[channelName]
    }
    if (isArray && useData?.numOfPages && typeOf(useData?.data) === 'Array') {
      channelData.numOfPages = useData.numOfPages
      channelData.total = useData.total
      channelData.pages[useData.page] = useData.data
      channelData.loading = useData.numOfPages ? Object.keys(channelData.pages).length < useData.numOfPages : true
      channelData.data = Object.values(channelData.pages).flat()
      return
    }

    if (!channelData?.data?.findIndex)
      return

    const index = channelData.data
      ?.findIndex(({ id }) => id === useData.id)
    if (index >= 0) {
      channelData.data[index] = useData
      return
    }
    channelData.data.push(useData)
    if (!channelData.ids.includes(useData.id)) {
      channelData.ids.push(useData.id)
      channelData.total++
    }
  }

  sockets[url] = { socket, data }
}

async function reconnect(url) {
  const data = sockets[url]?.data
  if (!data) return
  const attempt = connectionAttempts[url] ?? 0

  if (queue[url])
    clearTimeout(queue[url])

  queue[url] = setTimeout(() => {
    if (data?.status === 'CONNECTED') return
    if (attempt >= maxConnectionAttempts && data.status !== 'CONNECTED') {
      data.status = 'ERROR'
      print(`WEBSOCKET: ${url}`, `\n>>> FAIL CONNECTION AFTER ${attempt} ATTEMPTS`)
      close(url)
    }
    else {
      connectionAttempts[url]++
      data.status = ''
      data.status = 'CONNECTING'
      print(`WEBSOCKET: ${url}`, `\n>>> RECONNECTING... ${attempt + 1} ATTEMPT`)
      open(url)
    }
  }, reconnectionDelay * (attempt + 1))
}

function close(url) {
  if (!sockets[url]) return
  delete connectionAttempts[url]
  delete queue[url]
  const data = sockets[url]?.data ?? {}
  const emptyData = clone(nullData)
  for (const key in emptyData)
    data[key] = emptyData[key]
  data.status = 'CLOSED'
}

function remove(url) {
  close(url)
  delete sockets[url]
}

function send(url, message) {
  const { socket } = sockets[url]
  if (!socket) return
  socket.send(message)
}

export default function connectWebSocket(config) {
  const { url } = config
  const hasInvalidUrl = url?.includes('/undefined')
  open(url)

  return {
    socket: computed(() => hasInvalidUrl ? clone(nullData) : sockets[url]?.data),
    send: message => !hasInvalidUrl && send(url, message),
    open: () => !hasInvalidUrl && open(url),
    close: () => !hasInvalidUrl && close(url),
    remove: () => !hasInvalidUrl && remove(url),
  }
}