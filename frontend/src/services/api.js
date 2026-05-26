import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('marketplace.access')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function getApi(path, config) {
  const res = await api.get(path, config)
  return res.data
}

export async function postApi(path, data, config) {
  const res = await api.post(path, data, config)
  return res.data
}
