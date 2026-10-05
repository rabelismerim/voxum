import api from './api'

const { apiHost, prod: inProduction, routerBaseUrl } = useAmbient()

function getSignStatus() {
  return api
    .get('/v1/drfmsal_sign_status/')
    .then(result => result?.profile || {})
}

function getUsers() {
  return useService('/v1/core/user/', {
    paginated: true,
    extraPagination: ({ user_voxum, status, isActive }) => ({
      user_voxum,
      status,
      isActive,
    }),
    errorMessage: 'ERROR ON {{ usersService > getUsers }}',
    mapItem: user => ({
      ...user,
      group: user?.groups?.[0]?.id,
    }),
  })
}

function getUser(id) {
  return api.get(`/v1/core/user/${id}/`)
}

async function updateUser(user) {
  const { id, group, isActive } = user
  const editingUser = {
    id,
    groups: [group],
    isActive,
  }
  return api.put(`/v1/core/user/${id}/`, editingUser)
}

function logout() {
  if (!inProduction) return
  redirectTo(`${apiHost}/${routerBaseUrl}/v1/logout/`)
}

async function getUserDetail() {
  return api.get('v1/core/user/detail/')
}

async function loginLocal(username, password) {
  const { token } = await api.post('/v1/auth/token/', { username, password })
  sessionStorage.setItem('APP_TOKEN', token)
  return getUserDetail()
}

async function getProfile(redirectUrl) {
  if (!inProduction) {
    const { localAuth, token } = useAmbient()
    if (localAuth && !token && !sessionStorage.getItem('APP_TOKEN'))
      return { authenticated: false, authorized: false, isActive: false }

    const userDetail = await getUserDetail()
    return {
      ...userDetail,
      userPermissions: userDetail?.userPermissions ?? [],
      authenticated: true,
      authorized: true,
      permissions: userDetail?.userPermissions?.map(({ codename }) => codename) ?? [],
    }
  }

  return getSignStatus().then(async (user) => {
    const { authenticated, authorized, isActive } = user || {}
    print('USER SIGN STATUS:', { user, cookies: document.cookie })

    if (authenticated && !isActive) {
      return user
    }

    if (
      (inProduction && (!authenticated || !authorized))
      || (!inProduction && !authorized)
    ) {
      redirectTo(`${apiHost}/${routerBaseUrl}/api/v1/drfmsal_sign_in/${routerBaseUrl}${redirectUrl ?? '/'}`)
      return
    }

    const userDetail = (isActive || !inProduction) ? await getUserDetail() : []
    print('LOGIN USER DATA:', { inProduction, user, userDetail, apiHost, routerBaseUrl })

    return {
      ...user,
      ...userDetail,
      permissions: userDetail?.userPermissions?.map(({ codename }) => codename) ?? [],
    }
  })
}

function getUserGroups() {
  return api.get('/v1/core/user/group/')
}

function getUserGuest() {
  return api.get('/v1/guest/')
}

function createGuest(guestData) {
  return api.post('/v1/guest/', guestData)
}

async function updateUserGuest(id, guestData) {
  return api
    .put(`/v1/guest/${id}/`, guestData)
    .then(result => result?.guest)
}

export default {
  getSignStatus,
  loginLocal,
  getProfile,
  logout,
  getUserGroups,
  getUsers,
  getUser,
  updateUser,
  getUserGuest,
  createGuest,
  updateUserGuest,
  getUserDetail,
}