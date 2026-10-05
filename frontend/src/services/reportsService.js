import api from './api'

function getReport(meetingId) {
  return api.get(`v1/report/meeting/${meetingId}/`)
}

function generateMeetingReport(meetingId, reportType) {
  return api.post('v1/report/meeting/', { meetingId, reportType })
}

function generateVotingReport(votingId, reportType) {
  return api.post('v1/report/voting/', { votingId, reportType })
}

function getOptions() {
  return api
    .get('/v1/meeting/options/')
    .then(result => ({
      meeting: result?.reportMeetingOptions?.options ?? [],
      voting: result?.reportVotingOptions?.options ?? [],
    }))
}

export default {
  getReport,
  generateMeetingReport,
  generateVotingReport,
  getOptions,
}