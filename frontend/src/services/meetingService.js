import api from './api'
import apiSilence from './apiSilence'
import guestService from './guestService'

function getMeetings() {
  return api.get('/v1/meeting/')
}

const paginationVoters = ({ filterBy, sortBy, classes, voted, notVoted, votingId }) => {
  const isLegalNumber = (filterBy ?? '').match(/^(\d|\.|-|\/)+$/)
  return {
    voted,
    not_voted: notVoted,
    classe: Object.entries(classes ?? {}).filter(([, value]) => value).map(([key]) => key),
    sortBy: sortBy ?? 'first_name',
    [isLegalNumber ? 'legal_number' : 'first_name']: isLegalNumber
      ? filterBy.replace(/[^\d]/g, '')
      : filterBy,
    voting_id: votingId,
  }
}

function getCreditors(meetingId, socket) {
  return useService(`/v1/creditor/meeting/${meetingId}/`, {
    paginated: true,
    socket,
    channel: 'creditorList',
    errorMessage: 'ERROR ON {{ meetingService > getCreditors }}',
    extraPagination: paginationVoters,
    mapItem: creditor => ({
      ...creditor,
      fullName: `${creditor?.guest?.user?.firstName ?? ''} ${creditor?.guest?.user?.lastName ?? ''}`.trim(),
      legalNumber: creditor?.guest?.entity?.legalNumber,
      dockOk: creditor?.dockOk,
      email: creditor?.guest?.user?.email,
      classeId: creditor?.classe?.id,
      votingIds: creditor?.votes?.map(voting => voting?.vote?.votingId) ?? [],
      representatives: creditor?.representatives
        ?.slice()
        ?.sort((a, b) => (a.priority ?? 0) - (b.priority ?? 0))
        ?.map(({ representative, priority }) => ({
          id: representative?.id,
          fullName: `${representative?.guest?.user?.firstName ?? ''} ${representative?.guest?.user?.lastName ?? ''}`.trim(),
          legalNumber: representative?.guest?.entity?.legalNumber,
          priority,
        })) ?? [],
    }),
  })
}

function getRepresentatives(meetingId, socket) {
  return useService(`/v1/meeting/representatives/${meetingId}/`, {
    paginated: true,
    socket,
    channel: 'representativesMeetingList',
    errorMessage: 'ERROR ON {{ meetingService > getRepresentatives }}',
    extraPagination: paginationVoters,
    mapItem: representative => ({
      ...representative,
      fullName: `${representative?.guest?.user?.firstName ?? ''} ${representative?.guest?.user?.lastName ?? ''}`.trim(),
      legalNumber: representative?.guest?.entity?.legalNumber,
      classeId: representative?.classe?.id,
      votingIds: representative?.votes?.map(voting => voting?.vote?.votingId) ?? [],
      isRepresentative: true,
    }),
  })
}

function getVoters(list) {
  const base = list === 'creditors' ? 'creditor/meeting' : 'meeting/representatives'
  return (meetingId, pagination, votingId) => {
    const { filterColumn, filterBy = '', classes = {}, voted, notVoted } = pagination
    const classeNames = Object.entries(classes)
      .filter(([, value]) => value)
      .map(([key]) => key)

    const isLegalNumber = filterBy.match(/^(\d|\.|-|\/)+$/)
    const localFilter = filterColumn
      ? { filterColumn, filterBy }
      : {
          filterColumn: isLegalNumber ? 'legal_number' : 'first_name',
          filterBy: isLegalNumber ? filterBy.replace(/[^\d]/g, '') : filterBy,
        }

    const localPagination = {
      sortBy: 'first_name',
      ...pagination,
      ...localFilter,
    }

    const appendFilter = (voted && votingId ? `&voted=${votingId}` : '')
      + (notVoted && votingId ? `&not_voted=${votingId}` : '')
      + (classeNames.length ? classeNames.map(name => `&classe=${name}`).join('') : '')

    return api
      .get(`/v1/${base}/${meetingId}/${controlPagination(localPagination) + appendFilter}`)
      .then(result => ({
        count: result?.data?.count ?? 0,
        items: result?.data?.results?.map(creditor => ({
          ...creditor,
          classeId: creditor?.classe?.id,
          votingIds: creditor?.votes?.map(voting => voting?.vote?.votingId) ?? [],
        })) ?? [],
      }))
  }
}

function getGroups() {
  return api.get('/v1/meeting/group/')
}

function postMeeting(meetingData) {
  const meeting = { ...meetingData }
  delete meeting.status
  return api.post('/v1/meeting/', meeting)
}

function getMeeting(id) {
  return api.get(`/v1/meeting/${id}/`)
}

function getMeetingByGuest(meetingId) {
  return apiSilence.get(`/v1/meeting/guest/detail/${meetingId}/`)
}

function updateMeeting(meeting) {
  return api.put(`/v1/meeting/${meeting.id}/`, meeting)
}

function suspendMeeting(meeting) {
  return api.put(`/v1/meeting/suspend/${meeting.id}/`, meeting)
}

function removeMeeting(meeting) {
  return api.delete(`/v1/meeting/${meeting.id}/`)
}

function getCategories() {
  return api.get('/v1/meeting/category/')
}

function createCategory(category) {
  return api.post('/v1/meeting/category/', category)
}

function getMappedClasses() {
  return api
    .get('/v1/meeting/class/')
    .then(result => (result ?? []).map(({ id, description }) => ({ label: description, value: id })))
}

function getClasses() {
  return api.get('/v1/meeting/class/')
}

function createClass(meetingClass) {
  return api.post('/v1/meeting/class/', { ...meetingClass })
}

function getMeetingOptions() {
  return api
    .get('/v1/meeting/options/')
    .then(result =>
      Object.fromEntries(
        Object.entries(result || {}).map(([key, { options }]) => [key, options])
      )
    )
}

async function createRepresentative(meetingId, { fullName = '', email, legalNumber }) {
  const [firstName, ...rest] = fullName.trim().split(' ')
  const lastName = rest.join(' ')

  const guestResponse = await guestService.newGuest({
    firstName,
    lastName,
    email,
    legalNumber,
    isRepresentative: true,
  })

  const guestId = guestResponse?.id
  if (!guestId) return

  return api.post('/v1/meeting/representatives/', { meetingId, guestId })
}

function getVotings(meetingId) {
  return api
    .get(`/v1/voting/meeting/${meetingId}/`)
    .then(result => (result?.data?.results ?? []).flatMap(({ description, results }) => [
      {
        description,
        isCount: true,
        results: (results ?? []).map(({ name, choices }) => {
          const totalVoters = choices?.reduce((acc, { countVoters }) => acc + countVoters, 0) || 1
          return {
            name,
            choices: (choices ?? []).map(({ value, countVoters }) => ({
              option: value,
              value: (countVoters / totalVoters).toFixed(2),
            })),
          }
        }),
      },
      {
        description,
        isCount: false,
        results: (results ?? []).map(({ name, choices }) => {
          const totalAmount = choices?.reduce((acc, { totalVotersCreditValue }) => acc + totalVotersCreditValue, 0) || 1
          return {
            name,
            choices: (choices ?? []).map(({ value, totalVotersCreditValue }) => ({
              option: value,
              value: (totalVotersCreditValue / totalAmount).toFixed(2),
            })),
          }
        }),
      },
    ]))
}

function getOptions() {
  return api.get('/v1/meeting/options/')
}

function getBigNumbers(meetingId) {
  return api.get(`/v1/meeting/big_numbers/${meetingId}/`)
}

function sendAccessEmail(meetingId) {
  return api.post(`/v1/meeting/dispatch_link_meeting/${meetingId}/`)
}

function sendRegisterEmail(meetingId) {
  return api.post(`/v1/meeting/dispatch_link_ciam/${meetingId}/`)
}

export default {
  postMeeting,
  getMeeting,
  getVoters,
  getMeetingByGuest,
  getMeetings,
  getGroups,
  updateMeeting,
  suspendMeeting,
  removeMeeting,
  getCategories,
  createCategory,
  getClasses,
  getMappedClasses,
  createClass,
  getMeetingOptions,
  getRepresentatives,
  getCreditors,
  createRepresentative,
  getVotings,
  getOptions,
  getBigNumbers,
  sendAccessEmail,
  sendRegisterEmail,
}