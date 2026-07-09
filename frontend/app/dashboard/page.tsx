'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { FolderOpen, Globe, Activity, Clock, Plus, Rocket, Shield, Zap } from 'lucide-react'
import Link from 'next/link'
import { Navbar } from '@/components/navbar'
import { Sidebar } from '@/components/sidebar'
import { StatsCard } from '@/components/stats-card'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { projectsApi, crawlApi, Project, CrawlJob } from '@/lib/api'
import { formatDate } from '@/lib/utils'

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [jobs, setJobs] = useState<CrawlJob[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([projectsApi.list(), crawlApi.list()])
      .then(([projectsRes, jobsRes]) => {
        setProjects(projectsRes.data)
        setJobs(jobsRes.data)
      })
      .finally(() => setLoading(false))
  }, [])

  const stats = {
    total: projects.length,
    ready: projects.filter((p) => p.status === 'ready').length,
    crawling: jobs.filter((j) => j.status === 'running' || j.status === 'queued').length,
    assets: projects.reduce((acc, p) => acc + (p.stats?.assets || 0), 0),
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
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <h1 className="text-3xl font-black tracking-tight text-white">
                  Dashboard <span className="text-red-500">.</span>
                </h1>
                <p className="text-white/50">Overview of your cloning workspace</p>
              </div>
              <Link href="/projects">
                <Button className="gap-2 bg-red-600 hover:bg-red-700 text-white shadow-[0_0_20px_rgba(220,38,38,0.35)]">
                  <Plus className="h-4 w-4" /> New project
                </Button>
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
            >
              <StatsCard title="Total projects" value={stats.total} icon={FolderOpen} />
              <StatsCard title="Ready exports" value={stats.ready} icon={Globe} />
              <StatsCard title="Active jobs" value={stats.crawling} icon={Activity} />
              <StatsCard title="Assets downloaded" value={stats.assets} icon={Clock} />
            </motion.div>

            <div className="mt-8 grid gap-6 lg:grid-cols-3">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="lg:col-span-2"
              >
                <Card className="h-full border-white/5 bg-black/50 backdrop-blur-md">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                      <CardTitle className="text-white">Recent projects</CardTitle>
                      <p className="text-sm text-white/40">Your latest clone jobs</p>
                    </div>
                    <Rocket className="h-5 w-5 text-red-500" />
                  </CardHeader>
                  <CardContent>
                    {loading ? (
                      <p className="text-white/40">Loading...</p>
                    ) : projects.length === 0 ? (
                      <div className="py-10 text-center">
                        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-red-500/10 text-red-500">
                          <FolderOpen className="h-8 w-8" />
                        </div>
                        <h3 className="mt-4 text-lg font-semibold text-white">No projects yet</h3>
                        <p className="text-sm text-white/40">Create a project to start cloning a website you own.</p>
                        <Link href="/projects">
                          <Button variant="outline" className="mt-4 border-red-500/30 text-red-400 hover:bg-red-500/10">
                            Create your first project
                          </Button>
                        </Link>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {projects.slice(0, 5).map((project) => (
                          <Link
                            key={project.id}
                            href={`/projects/${project.id}`}
                            className="group flex items-center justify-between rounded-xl border border-white/5 bg-white/[0.02] p-4 transition-all hover:border-red-500/30 hover:bg-white/[0.05]"
                          >
                            <div className="flex items-center gap-4">
                              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10 text-red-500 group-hover:bg-red-500/20">
                                <Globe className="h-5 w-5" />
                              </div>
                              <div>
                                <p className="font-semibold text-white">{project.name}</p>
                                <p className="text-xs text-white/40">{project.source_url}</p>
                              </div>
                            </div>
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
                          </Link>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <Card className="h-full border-white/5 bg-black/50 backdrop-blur-md">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                      <CardTitle className="text-white">Active jobs</CardTitle>
                      <p className="text-sm text-white/40">Live crawl progress</p>
                    </div>
                    <Zap className="h-5 w-5 text-red-500" />
                  </CardHeader>
                  <CardContent>
                    {jobs.filter((j) => j.status === 'running' || j.status === 'queued').length === 0 ? (
                      <div className="py-10 text-center">
                        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-white/5 text-white/40">
                          <Shield className="h-8 w-8" />
                        </div>
                        <p className="mt-4 text-sm text-white/40">No active jobs</p>
                      </div>
                    ) : (
                      <div className="space-y-5">
                        {jobs
                          .filter((j) => j.status === 'running' || j.status === 'queued')
                          .slice(0, 5)
                          .map((job) => (
                            <div key={job.id} className="space-y-2">
                              <div className="flex items-center justify-between text-sm">
                                <span className="font-medium text-white">{job.status}</span>
                                <span className="text-red-400">{job.progress}%</span>
                              </div>
                              <Progress value={job.progress} />
                              <p className="text-xs text-white/40">
                                {job.crawled_pages} / {job.total_pages} pages · {job.downloaded_assets} assets
                              </p>
                            </div>
                          ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
