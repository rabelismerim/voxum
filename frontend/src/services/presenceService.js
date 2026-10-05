import api from './api'

function start(meetingId, duration) {
  return api.put(`/v1/meeting/register_presence/start/${meetingId}/`, { time: duration })
}

function extend(meetingId, duration) {
  return api.put(`/v1/meeting/register_presence/extend/${meetingId}/`, { time: duration })
}

function finish(meetingId) {
  return api.put(`/v1/meeting/register_presence/end/${meetingId}/`)
}

function registerVoterPresence(voter) {
  const isRep = Boolean(voter?.isRepresentative)
  const endpoint = `/v1/presence/${isRep ? 'representatives/' : ''}`
  const payload = {
    [isRep ? 'representativeId' : 'creditorId']: voter?.id,
  }

  return api.post(endpoint, payload)
}

function registerPresence(meetingId) {
  return api.post(`/v1/presence/guest/${meetingId}/`)
}

export default {
  start,
  extend,
  finish,
  registerPresence,
  registerVoterPresence,
}