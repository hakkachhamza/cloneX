'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, FolderOpen, History, Settings, Bell, FileText } from 'lucide-react'
import { cn } from '@/lib/utils'

const nav = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: FolderOpen },
  { name: 'History', href: '/history', icon: History },
  { name: 'Logs', href: '/logs', icon: FileText },
  { name: 'Notifications', href: '/notifications', icon: Bell },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  return (
    <aside className="relative z-20 hidden w-64 shrink-0 border-r border-white/5 bg-black/60 backdrop-blur-xl lg:block">
      <div className="p-4">
        <Link href="/dashboard" className="flex items-center gap-3 px-3 py-2">
          <img
            src="/logo.png"
            alt="cloneX"
            className="h-9 w-auto object-contain drop-shadow-[0_0_12px_rgba(220,38,38,0.5)]"
          />
          <span className="text-xl font-black tracking-wider text-white">
            clone<span className="text-red-500">X</span>
          </span>
        </Link>
      </div>
      <nav className="flex flex-col gap-1 p-4 pt-0">
        {nav.map((item) => {
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`)
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                active
                  ? 'bg-red-500/10 text-red-400'
                  : 'text-white/50 hover:bg-white/5 hover:text-white'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
