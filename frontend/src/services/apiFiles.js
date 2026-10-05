import axios from 'axios'

const { token, apiHost, apiBaseUrl, logRequest } = useAmbient()

const headers = {
  'Accept-Language': 'pt-BR,pt;q=1',
}

if (token) {
  headers.Authorization = `Token ${token}`
}

const apiFiles = axios.create({
  baseURL: `${apiHost}/${apiBaseUrl}`,
  withCredentials: true,
  xsrfHeaderName: 'X-CSRFToken',
  xsrfCookieName: 'csrftoken',
  timeout: 100000,
  headers,
})

apiFiles.interceptors.request.use((request) => {
  const { method, baseURL = '', url = '' } = request

  if (logRequest) {
    print(`>>>> REQUEST: ${method?.toUpperCase()} ${baseURL + url}`, request)
  }

  return request
})

apiFiles.interceptors.response.use(
  response => response.data,
  async (error) => {
    const { message, code, response } = error
    const errors = response?.data?.data?.errors ?? response?.data?.data
    const status = response?.status || 500

    print('ON ERROR:', errors)

    if (errors?.length > 0) {
      const newError = new Error(message)
      newError.errors = errors.map(({ detail }) => detail)
      newError.status = status
      newError.code = code
      throw newError
    }

    const mainErrors = {
      403: 'Você não está autorizado...',
      500: 'Problemas no Servidor...',
      ERR_NETWORK: 'Problemas no Servidor...',
    }

    const mainMessage = mainErrors[status] || mainErrors[code]
    if (mainMessage) {
      const newError = new Error(mainMessage)
      newError.errors = [mainMessage]
      newError.status = status
      newError.code = code
      throw newError
    }

    throw error
  }
)

export default apiFiles