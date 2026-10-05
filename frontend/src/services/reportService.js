import api from './api'

function getReport(meetingId) {
  return api.get(`/v1/report/meeting/${meetingId}/`)
}

function getReportMeeting(id) {
  return api.get(`/v1/report/meeting/detail/${id}/`)
}

function createReportMeeting(payload) {
  return api.post('/v1/report/meeting/', payload)
}

export default {
  getReport,
  getReportMeeting,
  createReportMeeting,
}