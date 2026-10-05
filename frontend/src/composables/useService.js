import { ref, watch } from 'vue'
import usePagination from './usePagination'
import { controlPagination, typeOf, print, isSame, clone } from './useUtils'
import api from '@/services/api'
import apiSilence from '@/services/apiSilence'

export default function useService(endpoint, options = {}) {
  if (endpoint.includes('/undefined'))
    return {
      pagination: {
        offset: 0,
        limit: 10,
        filterColumn: '',
        filterBy: '',
      },
      loading: false,
      items: [],
      updatePagination: _ => _,
      get: _ => _,
    }

  const {
    method = 'get',
    paginated = false,
    args = {},
    silence = false,
    mapItem = data => data,
    socket = ref({ channels: {} }),
    channel = '',
    extraPagination = {},
    errorMessage = 'ERROR ON {{ useService }}',
  } = options

  const needArgs = endpoint?.match(/(\{.+?\})/g)?.length > 0
  const url = args => endpoint?.replace(/(\{.+?\})/g, (match) => args[match?.slice(1, -1)]) ?? endpoint
  const useApi = silence ? apiSilence : api
  const localArgs = ref(args)

  if (!paginated) {
    return async (args) => {
      const { body } = args
      localArgs.value = args
      try {
        const result = await useApi[method](url(args), body)
        return { data: result?.data ?? result }
      } catch (error) {
        return { error }
      }
    }
  }

  const items = ref([])
  const loading = ref(false)
  const dumbFn = _ => _
  const loadEvents = ref({
    start: dumbFn,
    end: dumbFn,
  })
  const onLoad = ({ start, end }) => {
    loadEvents.value.start = start
    loadEvents.value.end = end
  }
  const disableLoading = ref(false)
  const { pagination, setTotal, updatePagination, ...rest } = usePagination()

  async function get(args = {}) {
    localArgs.value = args
    if (!disableLoading.value) {
      loading.value = true
      loadEvents.value.start?.()
    }

    let tryItems
    let resultItems
    try {
      const useUrl = url(args) + controlPagination(pagination.value, typeOf(extraPagination) === 'Object' ? extraPagination : extraPagination(pagination.value, args))
      const result = await useApi.get(useUrl)
      const data = result?.data ?? result
      setTotal(data?.count ?? 0)
      resultItems = data?.results ?? []
      tryItems = data?.results?.map(mapItem)
    } catch (error) {
      print(errorMessage + ': ', error)
    }
    finally {
      items.value = tryItems ?? resultItems ?? []
      loading.value = false
      loadEvents.value.end?.()
    }
  }

  const reloadItems = () => {
    if (!needArgs || Object.entries(localArgs.value)?.length > 0)
      get(localArgs.value ?? {})
  }

  let lastPagination = null
  watch(() => pagination, pagination => {
    if (!isSame(pagination?.value, lastPagination))
      reloadItems()
    lastPagination = clone(pagination?.value)
  }, { deep: true })

  if (channel && socket) {
    watch(() => [socket?.channels, socket?.value?.channels], ([channels1, channels2]) => {
      const channels = channels1 ?? channels2 ?? {}
      const channelData = channels?.[channel]
      if (!channelData) return
      const { type, data } = channelData ?? {}
      const dataId = data?.id
      if (!channel || !type || !dataId) return
      if (type === 'create' && items.value?.length < pagination.value?.rowsPerPage)
        reloadItems()
      if (type === 'update' || type === 'patch') {
        const index = items.value?.findIndex(({ id }) => id === dataId)
        if (index > -1) {
          const useItem = mapItem(data)
          if (useItem && type === 'update')
            items.value[index] = useItem
          else if (useItem && type === 'patch') {
            for (const key in useItem)
              items.value[index][key] = useItem[key]
          }
          else items.value.splice(index, 1)
        }
        else if (items.value?.length < pagination.value?.rowsPerPage)
          reloadItems()
      }
      if (type === 'delete')
        reloadItems()
    }, { deep: true })
  }

  return {
    ...rest,
    get,
    loading,
    onLoad,
    items,
    pagination,
    updatePagination,
  }
}
