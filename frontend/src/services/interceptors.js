const { logRequest, logResponse } = useAmbient()

export function requestInterceptor(request) {
  const { method, baseURL = '', url = '', data } = request
  const token = sessionStorage.getItem('APP_TOKEN') || useAmbient().token

  if (token)
    request.headers.Authorization = `Token ${token}`
  else
    delete request.headers.Authorization

  if (data) {
    request.data = parseToSnake(data)
  }

  if (logRequest) {
    print(`>>>> REQUEST: ${method?.toUpperCase()} ${baseURL + url}`, request)
  }

  return request
}

export function responseInterceptor(response) {
  const { data, status, config: { method, baseURL = '', url = '' } = {} } = response

  const result = parseToCamel(data)
  if (logResponse) {
    print(`<<<< RESPONSE(${status}): ${method?.toUpperCase()} ${baseURL + url}`, result)
  }

  return result
}

export async function errorHandlerInterceptor(error) {
  const { message, code, response } = error
  const data = response?.data?.data
  const status = response?.status || 500

  const { errors: dataErrors } = parseToCamel(data || {})
  const errors = dataErrors ? dataErrors.map(({ detail, attr }) => ({ message: detail, attr })) : data
  print('ON ERROR:', errors)

  if (errors?.length > 0) {
    for (const err of errors) {
      throwError({ id: code, message: err.message })
      await delay(0.5)
    }

    const newError = new Error(message)
    newError.errors = errors
    newError.status = status
    newError.code = code

    throw newError
  }

  const mainErrors = {
    403: 'Você não está autorizado...',
    500: 'Problemas no Servidor...',
    ERR_NETWORK: 'Problemas no Servidor...',
  }

  const mainMessage = data?.detail ?? (mainErrors[status] || mainErrors[code])
  if (mainMessage) {
    throwError({
      id: status,
      message: mainMessage,
    })

    const newError = new Error(mainMessage)
    newError.status = status
    newError.code = code

    throw newError
  }

  throw error
}

export function errorSilenceHandlerInterceptor(error) {
  const { response } = error
  const data = response?.data?.data
  const status = response?.status || 500

  const { errors: dataErrors } = parseToCamel(data || {})
  const errors = dataErrors ? dataErrors.map(({ detail, attr }) => ({ message: detail, attr })) : data
  print('ON ERROR:', { status, errors })
}