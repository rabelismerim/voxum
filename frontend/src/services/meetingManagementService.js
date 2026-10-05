import api from './api'

function getUsers(meetingId) {
  return api.get(`/v1/meeting/manager/users/${meetingId}/`)
}

function getUsersDetail(id) {
  return api.get(`/v1/meeting/manager/users/detail/${id}/`)
}

async function updateUsersDetail(id) {
  return api
    .put(`/v1/meeting/manager/users/detail/${id}/`)
    .then(result => result?.users)
}

function createUsers(userData) {
  return api.post('/v1/meeting/manager/users/', userData)
}

export default {
  getUsers,
  getUsersDetail,
  updateUsersDetail,
  createUsers,
}