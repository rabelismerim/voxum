import api from './api'

async function newCreditors(creditor) {
  const { recoverings, meetingId, classeId, coinType } = creditor
  if (!recoverings?.length) return []

  try {
    const requests = recoverings.map(recoveringId =>
      api.post('/v1/creditor/', {
        ...creditor,
        meetingId,
        classeId,
        recoveringId,
        coin: { coinType },
      })
    )

    const responses = await Promise.all(requests)
    return responses.map(res => res?.creditor).filter(Boolean)
  } catch (error) {
    print('ERROR ON NEW CREDITOR', error)
    throw error
  }
}

async function updateCreditor(creditor) {
  const localCreditor = {
    ...creditor,
    representatives: (creditor.representatives || []).map((representative, index) => ({
      representativeId: representative.id,
      priority: index,
    })),
  }
  return api.put(`/v1/creditor/${creditor.id}/`, localCreditor)
}

async function deleteCreditor(creditorId) {
  try {
    const response = await api.delete(`/v1/creditor/${creditorId}/`)
    return response?.data ?? response
  } catch (error) {
    console.error('ERROR ON DELETING CREDITOR', error)
    throw error
  }
}

export default {
  newCreditors,
  updateCreditor,
  deleteCreditor,
}