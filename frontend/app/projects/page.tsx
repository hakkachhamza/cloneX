'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { FolderOpen, Globe, MoreHorizontal, Plus, Trash2, Play } from 'lucide-react'
import { Navbar } from '@/components/navbar'
import { Sidebar } from '@/components/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { projectsApi, crawlApi, Project } from '@/lib/api'
import { formatDate } from '@/lib/utils'

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({ name: '', source_url: '', export_format: 'html' })
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = () => {
    projectsApi.list().then((res) => {
      setProjects(res.data)
      setLoading(false)
    })
  }

  const createProject = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    try {
      const res = await projectsApi.create({
        name: form.name,
        source_url: form.source_url,
        export_format: form.export_format,
        replacements: {
          company_name: '{{COMPANY_NAME}}',
          email: '{{EMAIL}}',
          phone: '{{PHONE}}',
          address: '{{ADDRESS}}',
          copyright: '{{COPYRIGHT}}',
          project_name: form.name,
        },
      })
      setOpen(false)
      setForm({ name: '', source_url: '', export_format: 'html' })
      await crawlApi.start(res.data.id, { max_depth: 3, max_pages: 30, respect_robots: true })
      loadProjects()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create project')
    } finally {
      setCreating(false)
    }
  }

  const deleteProject = async (id: string) => {
    if (!confirm('Delete this project?')) return
    await projectsApi.delete(id)
    loadProjects()
  }

  return (
    <div className="relative flex min-h-screen bg-background">
      <div className="fixed inset-0 z-0 bg-hero">
        <div className="absolute inset-0 bg-hero-overlay" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-red-900/15 via-transparent to-transparent" />
      </div>

      <Sidebar />
      <div className="relative z-10 flex flex-1 flex-col">
        <Navbar />
        <main className="flex-1 p-6">
          <div className="mx-auto max-w-7xl">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h1 className="text-3xl font-black tracking-tight text-white">
                  Projects <span className="text-red-500">.</span>
                </h1>
                <p className="text-white/50">Manage and clone authorized websites</p>
              </div>
              <Button onClick={() => setOpen(true)} className="gap-2 bg-red-600 hover:bg-red-700 text-white shadow-[0_0_20px_rgba(220,38,38,0.35)]">
                <Plus className="h-4 w-4" /> New project
              </Button>
            </div>

            {loading ? (
              <p className="mt-8 text-white/40">Loading...</p>
            ) : projects.length === 0 ? (
              <Card className="mt-8 border-white/5 bg-black/50 py-16 text-center backdrop-blur-md">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-red-500/10 text-red-500">
                  <FolderOpen className="h-8 w-8" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-white">No projects yet</h3>
                <p className="mt-1 text-sm text-white/40">Create a project to start cloning a website you own.</p>
                <Button onClick={() => setOpen(true)} className="mt-6 bg-red-600 hover:bg-red-700 text-white">
                  Create project
                </Button>
              </Card>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
              >
                <AnimatePresence>
                  {projects.map((project) => (
                    <motion.div
                      key={project.id}
                      layout
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                    >
                      <Card className="group h-full border-white/5 bg-black/50 backdrop-blur-md transition-all hover:border-red-500/30 hover:bg-black/70">
                        <CardHeader className="pb-3">
                          <div className="flex items-start justify-between">
                            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10 text-red-500">
                              <Globe className="h-5 w-5" />
                            </div>
                            <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                              <Link href={`/projects/${project.id}`}>
                                <Button variant="ghost" size="icon" className="text-white/50 hover:text-white hover:bg-white/5">
                                  <MoreHorizontal className="h-4 w-4" />
                                </Button>
                              </Link>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => deleteProject(project.id)}
                                className="text-white/50 hover:text-red-400 hover:bg-red-500/10"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                          <CardTitle className="mt-3 truncate text-lg text-white">{project.name}</CardTitle>
                          <p className="truncate text-xs text-white/40">{project.source_url}</p>
                        </CardHeader>
                        <CardContent>
                          <div className="flex items-center justify-between">
                            <Badge
                              variant={
                                project.status === 'ready'
                                  ? 'success'
                                  : project.status === 'failed'
                                  ? 'destructive'
                                  : 'default'
                              }
                            >
                              {project.status}
                            </Badge>
                            <span className="text-xs text-white/40">{formatDate(project.created_at)}</span>
                          </div>
                          <div className="mt-4 flex gap-2">
                            <Link href={`/projects/${project.id}`} className="flex-1">
                              <Button variant="outline" className="w-full border-white/10 bg-white/5 text-white hover:bg-white/10 hover:text-white">
                                Open
                              </Button>
                            </Link>
                            {project.status !== 'running' && project.status !== 'queued' && (
                              <Button
                                size="sm"
                                className="flex-1 gap-1 bg-red-600 hover:bg-red-700 text-white"
                                onClick={() => crawlApi.start(project.id).then(loadProjects)}
                              >
                                <Play className="h-3 w-3" /> Re-run
                              </Button>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </motion.div>
            )}
          </div>
        </main>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTitle className="text-white">New clone project</DialogTitle>
        <DialogDescription className="text-white/50">
          Enter the URL of a website you own or are authorized to clone.
        </DialogDescription>
        <form onSubmit={createProject} className="mt-4 space-y-4">
          <div>
            <Label htmlFor="name" className="text-white/80">Project name</Label>
            <Input
              id="name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
              className="mt-1.5 border-white/10 bg-white/5 text-white placeholder:text-white/30 focus-visible:ring-red-500"
            />
          </div>
          <div>
            <Label htmlFor="url" className="text-white/80">Website URL</Label>
            <Input
              id="url"
              type="url"
              placeholder="https://example.com"
              value={form.source_url}
              onChange={(e) => setForm({ ...form, source_url: e.target.value })}
              required
              className="mt-1.5 border-white/10 bg-white/5 text-white placeholder:text-white/30 focus-visible:ring-red-500"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="ghost" onClick={() => setOpen(false)} className="text-white/60 hover:text-white hover:bg-white/5">
              Cancel
            </Button>
            <Button type="submit" className="bg-red-600 hover:bg-red-700 text-white" isLoading={creating}>
              Create & clone
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  )
}
