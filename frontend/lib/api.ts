import axios, { AxiosError } from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export interface User {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  is_superuser: boolean
  created_at: string
}

export interface Project {
  id: string
  owner_id: string
  name: string
  source_url: string
  status: string
  storage_path: string | null
  stats: Record<string, any>
  replacements: Record<string, any>
  export_format: string
  created_at: string
  updated_at: string
}

export interface CrawlJob {
  id: string
  project_id: string
  celery_task_id: string | null
  status: string
  progress: number
  total_pages: number
  crawled_pages: number
  downloaded_assets: number
  errors: string[]
  logs: string[]
  options: Record<string, any>
  created_at: string
  updated_at: string
}

export const authApi = {
  login: (email: string, password: string) => {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)
    return api.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  register: (data: { email: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  me: () => api.get<User>('/users/me'),
}

export const projectsApi = {
  list: () => api.get<Project[]>('/projects/'),
  get: (id: string) => api.get<Project>(`/projects/${id}`),
  create: (data: { name: string; source_url: string; export_format?: string; replacements?: Record<string, any>; options?: Record<string, any> }) =>
    api.post<Project>('/projects/', data),
  update: (id: string, data: Partial<Project>) => api.put<Project>(`/projects/${id}`, data),
  delete: (id: string) => api.delete(`/projects/${id}`),
}

export const crawlApi = {
  list: () => api.get<CrawlJob[]>('/crawl/'),
  get: (id: string) => api.get<CrawlJob>(`/crawl/${id}`),
  start: (project_id: string, options?: Record<string, any>) =>
    api.post<CrawlJob>('/crawl/', { project_id, options }),
  pause: (id: string) => api.patch<CrawlJob>(`/crawl/${id}/pause`),
  resume: (id: string) => api.patch<CrawlJob>(`/crawl/${id}/resume`),
  cancel: (id: string) => api.patch<CrawlJob>(`/crawl/${id}/cancel`),
}
