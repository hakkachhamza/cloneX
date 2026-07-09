'use client'

import { Navbar } from '@/components/navbar'
import { Sidebar } from '@/components/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Bell } from 'lucide-react'

export default function NotificationsPage() {
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
              Notifications <span className="text-red-500">.</span>
            </h1>
            <p className="text-white/50">Stay updated on your clone jobs</p>
            <Card className="mt-6 border-white/5 bg-black/50 py-16 text-center backdrop-blur-md">
              <Bell className="mx-auto h-12 w-12 text-white/30" />
              <h3 className="mt-4 text-lg font-semibold text-white">No notifications</h3>
              <p className="text-sm text-white/40">Notifications will appear when jobs complete or fail.</p>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
