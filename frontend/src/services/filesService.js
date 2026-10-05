import api from './api'
import apiFiles from './apiFiles'

function getFileDetail(id) {
  return api.get(`/v1/process_file/detail/${id}/`)
}

function getFiles(objectId) {
  return api.get(`/v1/process_file/list/${objectId}/`)
}

function getExampleNames() {
  return api
    .get('/v1/process_file/examples/name/')
    .then(result => result?.map(item => item.name) ?? [])
}

function getExampleFile(name) {
  return apiFiles.get(`/v1/process_file/examples/detail/${name}/`, { responseType: 'blob' })
}

async function newCreateFile(createFile, path) {
  const { file, objectId, name } = createFile
  try {
    const result = await api.post(`/v1/process_file/create/${path}/${name}/`, {
      file,
      objectId,
      name,
      path,
    })
    return [result?.createFile].filter(Boolean)
  } catch (error) {
    print('ERROR ON NEW CREATE PATH', error)
    throw error
  }
}

export default {
  getFileDetail,
  getFiles,
  getExampleNames,
  getExampleFile,
  newCreateFile,
}