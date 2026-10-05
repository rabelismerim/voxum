import api from './api'

function getRecoverings() {
  return api
    .get('/v1/recovering/')
    .then(result => result?.recoverings ?? [])
}

async function newRecovering(recovering) {
  const { name } = recovering || {}
  try {
    const result = await api
      .post('/v1/recovering/', { name })
      .then(res => res?.recovering)

    return result ? [result] : []
  } catch (error) {
    print('ERROR ON NEW RECOVERING', error)
    throw error
  }
}

export default {
  getRecoverings,
  newRecovering,
}