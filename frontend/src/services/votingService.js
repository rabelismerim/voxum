import api from './api'

const votingStatusColors = {
  I: '#007db3', // iniciada
  A: '#7e7e7e', // Agendada
  E: '#007cb0', // encerrada
  R: '#FFD700', // reagendada
}

function getRepresentativeCreditors({ offset: offSet, limit, classe, representativeId, votingId }) {
  return api
    .get(`/v1/creditor/representative/${representativeId}/?offset=${offSet}&limit=${limit}&classe=${classe}&voting=${votingId}`)
    .then(result => ({
      count: result?.data?.count ?? 0,
      items: (result?.data?.results ?? [])
        .filter(creditor => creditor?.isAccredited)
        .map((creditor) => {
          const vote = creditor?.votes?.find(v => v?.vote?.votingId === votingId)
          return {
            id: creditor?.id,
            name: `${creditor?.guest?.user?.firstName ?? ''} ${creditor?.guest?.user?.lastName ?? ''}`.trim(),
            email: creditor?.guest?.user?.email,
            legalNumber: creditor?.guest?.entity?.legalNumber,
            amount: creditor?.creditValue ?? 0,
            coin: creditor?.coin?.typeDisplay ?? 'BRL',
            classe: {
              id: creditor?.classe?.id,
              description: creditor?.classe?.description,
            },
            choice: vote?.vote?.id,
            hasReservations: vote?.hasReservations,
          }
        }),
    }))
}

function getVotings(meetingId, socket, statuses) {
  return useService(`/v1/voting/meeting/${meetingId}/`, {
    paginated: true,
    socket,
    channel: 'votingList',
    errorMessage: 'ERROR ON {{ votingService > getVotings }}',
    extraPagination: {
      status: statuses,
    },
    mapItem: (voting) => {
      if (!statuses?.length || statuses?.includes(voting?.status)) {
        return {
          ...voting,
          statusColor: votingStatusColors[voting?.status],
        }
      }
    },
  })
}

function create(voting) {
  return api.post('/v1/voting/', voting)
}

function update(voting) {
  const { choices = [], classList = [] } = voting || {}
  const options = clone(choices)

  const updatedVoting = {
    ...voting,
    choice: classList.flatMap(classeId =>
      options.map(value => ({ classeId, value }))
    ),
  }

  return api.put('/v1/voting/', updatedVoting)
}

function remove(voting) {
  return api.delete(`/v1/voting/${voting.id}/`)
}

function start(votingId, duration) {
  return api.put(`/v1/voting/start/${votingId}/`, { time: duration })
}

function extend(votingId, duration) {
  return api.put(`/v1/voting/extend/${votingId}/`, { time: duration })
}

function finish(votingId) {
  return api.put(`/v1/voting/end/${votingId}/`)
}

function creditorVote(creditorId, choiceId, hasReservations = false) {
  return api.post('/v1/voting/guest/result/', { creditorId, voteId: choiceId, hasReservations })
}

function representativeVote(meetingId, creditorsVoting) {
  return api.post('/v1/voting/guest/representatives/result/', { meetingId, creditorsVoting })
}

function voteForCreditor(creditorId, choiceId, hasReservations = false, result) {
  const method = result?.id ? 'put' : 'post'
  const url = `/v1/voting/result${result?.id ? `/${result.id}` : ''}/`
  return api[method](url, { creditorId, voteId: choiceId, hasReservations })
}

function voteForRepresentative(votingId, meetingId, creditorsVoting) {
  return api
    .post(`/v1/voting/representatives/${votingId}/`, { creditorsVoting, meetingId })
    .then(result => (result?.result ?? []).map(({ success }) => success))
}

function getVotingResults() {
  return useService('/v1/voting/qualified_creditors/{votingId}/', {
    paginated: true,
    errorMessage: 'ERROR ON {{ votingService > getVotingResults }}',
  })
}

export default {
  getRepresentativeCreditors,
  getVotings,
  create,
  update,
  start,
  remove,
  extend,
  finish,
  creditorVote,
  representativeVote,
  voteForCreditor,
  voteForRepresentative,
  getVotingResults,
}