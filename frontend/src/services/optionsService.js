import api from './api'

async function getOptions(...keys) {
  return api
    .get('v1/meeting/options/')
    .then(result => (keys?.length ? keys.map(key => result?.[key]?.options) : result))
}

export default {
  getOptions,
}