import api from './api'

function getGuest() {
  return api
    .get('/v1/guest/')
    .then(result => result?.guest)
}

async function newGuest(guest) {
  const { firstName, lastName, email, legalNumber } = guest
  return api.post('/v1/guest/', {
    ...guest,
    user: {
      firstName,
      lastName,
      email,
    },
    entity: {
      legalNumber,
    },
  })
}

export default {
  getGuest,
  newGuest,
}