import { computed } from 'vue'
import { useStorage } from '@vueuse/core'
import router from '@/router'
import { print, clone } from './useUtils'
import usersService from '@/services/usersService'
import useAmbient from './useambient'

const userFallback = {}

const store = useStorage('APP_USR', clone(userFallback), sessionStorage)

function storeUserProfile(user) {
  store.value = {
    ...store.value,
    ...user,
  }
  return store.value
}

async function login(redirectUrl) {
  try {
    const user = await usersService.getProfile(redirectUrl)

    print('ON LOGIN SUCCESS:', user)
    return storeUserProfile(user)
  }
  catch (error) {
    print('ERROR ON LOGIN:', error)
    if (!useAmbient().localAuth)
      router?.push({ path: '/' })
    throw error
  }
}

async function loginLocal(username, password) {
  try {
    const userDetail = await usersService.loginLocal(username, password)
    const user = {
      ...userDetail,
      authenticated: true,
      authorized: true,
      permissions: userDetail?.userPermissions?.map(({ codename }) => codename) ?? [],
    }

    print('ON LOCAL LOGIN SUCCESS:', user)
    return storeUserProfile(user)
  }
  catch (error) {
    print('ERROR ON LOCAL LOGIN:', error)
    throw error
  }
}

async function logout() {
  try {
    store.value = clone(userFallback)
    sessionStorage.removeItem('APP_TOKEN')
    usersService.logout()
  }
  catch (error) {
    print('ERROR ON LOGOUT:', error)
  }
}

const user = computed(() => store.value)
const isActive = computed(() => store.value.isActive)
const isAuthorized = computed(() => store.value.isActive)

function hasPermissions(...permissions) {
  return permissions
    .every(permission => store.value.permissions?.includes(permission))
}

function updateProfile(user) {
  store.value = { ...store.value, ...user }
}

export default {
  login,
  loginLocal,
  logout,
  user,
  isActive,
  isAuthorized,
  hasPermissions,
  updateProfile,
}