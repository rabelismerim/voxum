export function useAmbient() {
  const env = import.meta.env
  const routerBaseUrl = `/${(env.VITE_ROUTER_BASE_URL || 'voxum').replace(/^\/+|\/+$/g, '')}/`

  return {
    token: env.VITE_TOKEN || '',
    localAuth: env.MODE === 'devlocal',
    socketHost: env.VITE_SOCKET_HOST || '',
    socketPort: env.VITE_SOCKET_PORT || '',
    apiHost: (env.VITE_API_HOST || '').replace(/\/+$/, ''),
    apiBaseUrl: (env.VITE_API_BASE_URL || 'voxum/api').replace(/^\/+|\/+$/g, ''),
    baseUrl: (env.BASE_URL || '/').replace(/\/$/, ''),
    routerBaseUrl,
    prod: env.PROD,
    isDev: env.DEV,
    isMobile: () => typeof window !== 'undefined' && window.matchMedia('(max-width: 768px)').matches,
    logRequest: env.VITE_LOG_REQUEST === 'true',
    logResponse: env.VITE_LOG_RESPONSE === 'true',
  }
}

export default useAmbient