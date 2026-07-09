'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { LogOut, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { authApi } from '@/lib/api'

export function Navbar() {
  const router = useRouter()
  const [user, setUser] = useState<{ email: string; full_name: string | null } | null>(null)

  useEffect(() => {
    authApi.me().then((res) => setUser(res.data)).catch(() => setUser(null))
  }, [])

  const logout = () => {
    localStorage.removeItem('token')
    router.push('/login')
  }

  return (
    <header className="sticky top-0 z-40 glass-strong">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/dashboard" className="flex items-center gap-3">
          <img
            src="/logo.png"
            alt="cloneX"
            className="h-10 w-auto object-contain drop-shadow-[0_0_12px_rgba(220,38,38,0.5)]"
          />
          <span className="text-2xl font-black tracking-wider text-white text-glow">
            clone<span className="text-red-500">X</span>
          </span>
        </Link>
        <div className="flex items-center gap-4">
          {user && (
            <div className="hidden items-center gap-2 text-sm text-muted-foreground sm:flex">
              <User className="h-4 w-4" />
              {user.full_name || user.email}
            </div>
          )}
          <Button variant="ghost" size="sm" onClick={logout} className="text-muted-foreground hover:text-white hover:bg-red-500/10">
            <LogOut className="mr-2 h-4 w-4" />
            Log out
          </Button>
        </div>
      </div>
    </header>
  )
}
