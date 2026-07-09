'use client'

import { useEffect, useState } from 'react'
import { Navbar } from '@/components/navbar'
import { Sidebar } from '@/components/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { crawlApi, CrawlJob } from '@/lib/api'
import { formatDate } from '@/lib/utils'

export default function HistoryPage() {
  const [jobs, setJobs] = useState<CrawlJob[]>([])

  useEffect(() => {
    crawlApi.list().then((res) => setJobs(res.data))
  }, [])

  return (
    <div className="relative flex min-h-screen bg-background">
      <div className="fixed inset-0 z-0 bg-hero"><div className="absolute inset-0 bg-hero-overlay" /></div>
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-red-900/15 via-transparent to-transparent" />

      <Sidebar />
      <div className="relative z-10 flex flex-1 flex-col">
        <Navbar />
        <main className="flex-1 p-6">
          <div className="mx-auto max-w-7xl">
            <h1 className="text-3xl font-black tracking-tight text-white">
              History <span className="text-red-500">.</span>
            </h1>
            <p className="text-white/50">All crawl jobs across your projects</p>
            <Card className="mt-6 border-white/5 bg-black/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-white">Crawl history</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {jobs.map((job) => (
                    <div key={job.id} className="flex items-center justify-between rounded-xl border border-white/5 bg-white/[0.02] p-4">
                      <div>
                        <p className="font-semibold text-white">{job.status}</p>
                        <p className="text-xs text-white/40">{formatDate(job.created_at)}</p>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-white/60">
                        <span>{job.crawled_pages} pages</span>
                        <span>{job.downloaded_assets} assets</span>
                        <Badge variant={job.status === 'completed' ? 'success' : job.status === 'failed' ? 'destructive' : 'default'}>
                          {job.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                  {jobs.length === 0 && <p className="text-white/40">No history yet.</p>}
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
