import { createRouter, createWebHistory } from 'vue-router'
import { setupLayouts } from 'virtual:generated-layouts'
import generatedRoutes from '~pages'

const { routerBaseUrl } = useAmbient()

const routes = setupLayouts(generatedRoutes).map((route, index) => {
  route.meta = generatedRoutes[index]?.meta || {}
  return route
})

const router = createRouter({
  history: createWebHistory(routerBaseUrl),
  routes,
})

router.beforeEach((to, from, next) => {
  const permissions = to.meta?.permissions || []
  const authenticated = Boolean(to.meta?.authenticated)
  const notGuest = Boolean(to.meta?.notGuest)

  let user = {}
  try {
    user = JSON.parse(sessionStorage.getItem('APP_USR') || '{}')
  } catch (error) {
    console.error('Erro ao ler utilizador do sessionStorage:', error)
  }

  const { isActive, isUserGuest, permissions: userPermissions = [] } = user
  const hasAllPermissions = permissions.every(permission => userPermissions.includes(permission))

  print('=> ON ROUTER:', {
    to,
    from,
    permissions,
    authenticated,
    notGuest,
    isActive,
    isUserGuest,
    hasAllPermissions,
  })

  // Redirecionamento de convidados tentando aceder a rotas restritas
  if (notGuest && isUserGuest) {
    return next('/votacao')
  }

  // Validação de acesso a rotas públicas vs autenticadas/com permissão
  const isPublicRoute = !authenticated && permissions.length === 0
  const hasValidAuth = authenticated && isActive
  const hasValidPermissions = permissions.length > 0 && isActive && hasAllPermissions

  if (!isPublicRoute && !hasValidAuth && !hasValidPermissions) {
    throwError({
      message: 'Você não tem permissão de ver essa página!',
      id: 'UNAUTHORIZED',
    })
    return next('/')
  }

  return next()
})

export default router