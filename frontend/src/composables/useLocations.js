import { ref } from 'vue'
import locationService from '@/services/locationService'

const locations = ref([])
const loading = ref(false)

export default function useLocations() {
  async function loadLocations() {
    loading.value = true
    try {
      const result = await locationService.getLocations()
      if (!Array.isArray(result))
        throw new TypeError('The locations endpoint must return a list.')
      locations.value = result
      return locations.value
    }
    finally {
      loading.value = false
    }
  }

  async function addLocation(description) {
    const location = await locationService.postLocation({ description })
    locations.value.push(location)
    return location
  }

  return {
    locations,
    loading,
    loadLocations,
    addLocation,
  }
}
