'use client'

import { Navbar } from '@/components/navbar'
import { Sidebar } from '@/components/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function SettingsPage() {
  return (
    <div className="relative flex min-h-screen bg-background">
      <div className="fixed inset-0 z-0 bg-hero"><div className="absolute inset-0 bg-hero-overlay" /></div>
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-red-900/15 via-transparent to-transparent" />

      <Sidebar />
      <div className="relative z-10 flex flex-1 flex-col">
        <Navbar />
        <main className="flex-1 p-6">
          <div className="mx-auto max-w-3xl">
            <h1 className="text-3xl font-black tracking-tight text-white">
              Settings <span className="text-red-500">.</span>
            </h1>
            <p className="text-white/50">Manage your workspace preferences</p>

            <Card className="mt-6 border-white/5 bg-black/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-white">Profile</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="email" className="text-white/80">Email</Label>
                  <Input id="email" disabled defaultValue="admin@cloneforge.local" className="mt-1.5 border-white/10 bg-white/5 text-white" />
                </div>
                <div>
                  <Label htmlFor="name" className="text-white/80">Full name</Label>
                  <Input id="name" placeholder="Your name" className="mt-1.5 border-white/10 bg-white/5 text-white placeholder:text-white/30 focus-visible:ring-red-500" />
                </div>
                <Button className="bg-red-600 hover:bg-red-700 text-white">Save changes</Button>
              </CardContent>
            </Card>

            <Card className="mt-6 border-white/5 bg-black/50 backdrop-blur-md">
              <CardHeader>
                <CardTitle className="text-white">Security</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="current" className="text-white/80">Current password</Label>
                  <Input id="current" type="password" className="mt-1.5 border-white/10 bg-white/5 text-white focus-visible:ring-red-500" />
                </div>
                <div>
                  <Label htmlFor="new" className="text-white/80">New password</Label>
                  <Input id="new" type="password" className="mt-1.5 border-white/10 bg-white/5 text-white focus-visible:ring-red-500" />
                </div>
                <Button className="bg-red-600 hover:bg-red-700 text-white">Update password</Button>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
