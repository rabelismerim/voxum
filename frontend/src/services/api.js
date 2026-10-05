import axios from 'axios'
import { requestInterceptor, responseInterceptor, errorHandlerInterceptor } from './interceptors'

const { token, apiHost, apiBaseUrl } = useAmbient()

const headers = {
  'Accept-Language': 'pt-BR,pt;q=1',
}

if (token) {
  headers.Authorization = `Token ${token}`
}

const api = axios.create({
  baseURL: `${apiHost}/${apiBaseUrl}`,
  withCredentials: true,
  xsrfHeaderName: 'X-CSRFToken',
  xsrfCookieName: 'csrftoken',
  withXSRFToken: true,
  timeout: 100000,
  headers,
})

api.interceptors.request.use(requestInterceptor)
api.interceptors.response.use(responseInterceptor, errorHandlerInterceptor)

export { api }
export default api