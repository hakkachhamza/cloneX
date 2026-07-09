'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowLeft, Play, Pause, XCircle, Globe, ImageIcon, FileCode, Type } from 'lucide-react'
import Link from 'next/link'
import { Navbar } from '@/components/navbar'
import { Sidebar } from '@/components/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { projectsApi, crawlApi, Project, CrawlJob } from '@/lib/api'
import { formatDate } from '@/lib/utils'

export default function ProjectDetailPage() {
  const { id } = useParams() as { id: string }
  const [project, setProject] = useState<Project | null>(null)
  const [jobs, setJobs] = useState<CrawlJob[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    load()
    const interval = setInterval(load, 3000)
    return () => clearInterval(interval)
  }, [id])

  const load = () => {
    Promise.all([projectsApi.get(id), crawlApi.list()])
      .then(([projectRes, jobsRes]) => {
        setProject(projectRes.data)
        setJobs(jobsRes.data.filter((j) => j.project_id === id))
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }

  const latestJob = jobs[0]
  const stats = project?.stats || {}

  if (loading) {
    return (
      <div className="relative flex min-h-screen bg-background">
        <div className="fixed inset-0 z-0 bg-hero"><div className="absolute inset-0 bg-hero-overlay" /></div>
        <Sidebar />
        <div className="relative z-10 flex flex-1 flex-col">
          <Navbar />
          <main className="flex-1 p-6"><p className="text-white/40">Loading project...</p></main>
        </div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="relative flex min-h-screen bg-background">
        <div className="fixed inset-0 z-0 bg-hero"><div className="absolute inset-0 bg-hero-overlay" /></div>
        <Sidebar />
        <div className="relative z-10 flex flex-1 flex-col">
          <Navbar />
          <main className="flex-1 p-6"><p className="text-red-400">Project not found</p></main>
        </div>
      </div>
    )
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
              <div className="flex items-center gap-3">
                <Link href="/projects">
                  <Button variant="ghost" size="icon" className="text-white/60 hover:text-white hover:bg-white/5">
                    <ArrowLeft className="h-5 w-5" />
                  </Button>
                </Link>
                <div>
                  <h1 className="text-3xl font-black tracking-tight text-white">{project.name}</h1>
                  <p className="text-sm text-white/50">{project.source_url}</p>
                </div>
              </div>
              <div className="flex gap-2">
                {latestJob?.status === 'running' || latestJob?.status === 'queued' ? (
                  <>
                    <Button variant="outline" onClick={() => crawlApi.pause(latestJob.id).then(load)} className="border-white/10 bg-white/5 text-white hover:bg-white/10">
                      <Pause className="mr-2 h-4 w-4" /> Pause
                    </Button>
                    <Button variant="destructive" onClick={() => crawlApi.cancel(latestJob.id).then(load)}>
                      <XCircle className="mr-2 h-4 w-4" /> Cancel
                    </Button>
                  </>
                ) : (
                  <Button onClick={() => crawlApi.start(id).then(load)} className="bg-red-600 hover:bg-red-700 text-white">
                    <Play className="mr-2 h-4 w-4" /> Start crawl
                  </Button>
                )}
              </div>
            </div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
            >
              <Stat icon={Globe} label="Pages" value={stats.pages || 0} />
              <Stat icon={FileCode} label="Crawled" value={stats.crawled_pages || 0} />
              <Stat icon={ImageIcon} label="Assets" value={stats.assets || 0} />
              <Stat icon={Type} label="Errors" value={stats.errors || 0} />
            </motion.div>

            {latestJob && (
              <Card className="mt-6 border-white/5 bg-black/50 backdrop-blur-md">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-white">Job progress</CardTitle>
                    <Badge variant={latestJob.status === 'running' ? 'default' : latestJob.status === 'completed' ? 'success' : 'secondary'}>
                      {latestJob.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <Progress value={latestJob.progress} />
                  <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-white/40">Pages</p>
                      <p className="font-semibold text-white">{latestJob.crawled_pages} / {latestJob.total_pages}</p>
                    </div>
                    <div>
                      <p className="text-white/40">Assets</p>
                      <p className="font-semibold text-white">{latestJob.downloaded_assets}</p>
                    </div>
                    <div>
                      <p className="text-white/40">Started</p>
                      <p className="font-semibold text-white">{formatDate(latestJob.created_at)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            <Tabs defaultValue="original" className="mt-8">
              <TabsList className="bg-black/50 border border-white/5">
                <TabsTrigger value="original">Original preview</TabsTrigger>
                <TabsTrigger value="generated">Generated preview</TabsTrigger>
                <TabsTrigger value="split">Split screen</TabsTrigger>
              </TabsList>
              <TabsContent value="original">
                <PreviewFrame src={project.source_url} title="Original" />
              </TabsContent>
              <TabsContent value="generated">
                {project.status === 'ready' ? (
                  <PreviewFrame src={`/api/projects/${project.id}/preview`} title="Generated" />
                ) : (
                  <Card className="py-16 text-center border-white/5 bg-black/50 backdrop-blur-md">
                    <p className="text-white/50">Generated preview will appear after the crawl completes.</p>
                  </Card>
                )}
              </TabsContent>
              <TabsContent value="split">
                <div className="grid h-[600px] gap-4 lg:grid-cols-2">
                  <PreviewFrame src={project.source_url} title="Original" />
                  <PreviewFrame src={`/api/projects/${project.id}/preview`} title="Generated" />
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>
    </div>
  )
}

function Stat({ icon: Icon, label, value }: { icon: any; label: string; value: string | number }) {
  return (
    <Card className="gradient-border border-white/5 bg-black/50 backdrop-blur-md">
      <CardContent className="flex items-center gap-4 p-6">
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-red-500/10 text-red-500">
          <Icon className="h-6 w-6" />
        </div>
        <div>
          <p className="text-sm text-white/40">{label}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
        </div>
      </CardContent>
    </Card>
  )
}

function PreviewFrame({ src, title }: { src: string; title: string }) {
  return (
    <Card className="h-[600px] overflow-hidden border-white/5 bg-black/50 p-0 backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-white/5 px-4 py-3">
        <span className="text-sm font-semibold text-white">{title}</span>
        <a href={src} target="_blank" rel="noopener noreferrer" className="text-xs text-red-400 hover:text-red-300">
          Open in new tab
        </a>
      </div>
      <iframe src={src} title={title} className="h-full w-full border-0 bg-white" sandbox="allow-scripts allow-same-origin" />
    </Card>
  )
}
