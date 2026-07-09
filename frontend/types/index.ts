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
