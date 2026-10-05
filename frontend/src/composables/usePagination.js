import { ref, computed } from 'vue'

export default function usePagination() {
  const pagination = ref({
    page: 1,
    rowsPerPage: 10,
    rowsNumber: 0,
    filterBy: '',
    sortBy: '',
    descending: false,
  })
  const onFirstPage = computed(() => pagination.value.page <= 1)
  const onLastPage = computed(() => pagination.value.page >= Math.ceil(pagination.value.rowsNumber / pagination.value.rowsPerPage))

  const nextPage = () => {
    if (onLastPage.value) return
    pagination.value.page++
  }
  const previousPage = () => {
    if (onFirstPage.value) return
    pagination.value.page--
  }
  const setPage = (page) => {
    pagination.value.page = page
  }
  const resetPage = () => {
    pagination.value.page = 1
  }
  const setTotal = (total) => {
    pagination.value.rowsNumber = total
  }
  const updatePagination = (updateData = {}) => {
    Object.entries(updateData)
      .forEach(([key, value]) => pagination.value[key] = value)
  }
  return {
    pagination,
    onFirstPage,
    onLastPage,
    setPage,
    resetPage,
    nextPage,
    previousPage,
    setTotal,
    updatePagination,
  }
}