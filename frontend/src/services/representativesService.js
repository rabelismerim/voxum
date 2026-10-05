import api from './api'

function getRepresentatives(votingId, socket) {
  return useService(`/v1/meeting/representatives/voting/${votingId}/`, {
    paginated: true,
    socket,
    channel: 'representativesMeetingList',
    errorMessage: 'ERROR ON {{ representativesService > getRepresentatives }}',
    extraPagination: ({ filterBy, sortBy, classes, voted, notVoted }) => {
      const isLegalNumber = (filterBy ?? '').match(/^(\d|\.|-|\/)+$/)
      return {
        voted,
        not_voted: notVoted,
        classe: Object.entries(classes ?? {}).filter(([, value]) => value).map(([key]) => key),
        sortBy: sortBy ?? 'first_name',
        [isLegalNumber ? 'legal_number' : 'first_name']: isLegalNumber
          ? filterBy.replace(/[^\d]/g, '')
          : filterBy,
      }
    },
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

export default {
  getRepresentatives,
}