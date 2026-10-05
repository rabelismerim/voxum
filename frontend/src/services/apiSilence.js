import axios from 'axios'
import { requestInterceptor, responseInterceptor, errorSilenceHandlerInterceptor } from './interceptors'

const { token, apiHost, apiBaseUrl } = useAmbient()

const headers = {
  'Accept-Language': 'pt-BR,pt;q=1',
}

if (token) {
  headers.Authorization = `Token ${token}`
}

const apiSilence = axios.create({
  baseURL: `${apiHost}/${apiBaseUrl}`,
  withCredentials: true,
  xsrfHeaderName: 'X-CSRFToken',
  xsrfCookieName: 'csrftoken',
  timeout: 100000,
  headers,
})

apiSilence.interceptors.request.use(requestInterceptor)
apiSilence.interceptors.response.use(responseInterceptor, errorSilenceHandlerInterceptor)

export default apiSilence