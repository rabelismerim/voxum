import api from './api'

function getLocations() {
  return api.get('/v1/location/')
}

function postLocation(payload) {
  return api.post('/v1/location/', { ...payload })
}

export default {
  getLocations,
  postLocation,
}