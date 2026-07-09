'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, Shield, Zap, Globe, Lock, Layers } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function HomePage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-hero">
      <div className="absolute inset-0 bg-hero-overlay" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-red-900/20 via-transparent to-transparent" />

      <nav className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <Link href="/" className="flex items-center gap-3">
          <img
            src="/logo.png"
            alt="cloneX"
            className="h-12 w-auto object-contain drop-shadow-[0_0_16px_rgba(220,38,38,0.6)]"
          />
          <span className="text-3xl font-black tracking-wider text-white text-glow">
            clone<span className="text-red-500">X</span>
          </span>
        </Link>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-medium text-white/70 hover:text-white transition-colors">
            Sign in
          </Link>
          <Link href="/register">
            <Button className="bg-red-600 hover:bg-red-700 text-white shadow-[0_0_20px_rgba(220,38,38,0.4)]">
              Get started
            </Button>
          </Link>
        </div>
      </nav>

      <main className="relative z-10 mx-auto max-w-7xl px-6 pb-24 pt-16">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="text-center"
        >
          <div className="mx-auto mb-8 flex h-28 w-28 items-center justify-center rounded-2xl bg-black/40 p-3 ring-1 ring-red-500/30 shadow-[0_0_50px_rgba(220,38,38,0.35)]">
            <img src="/logo.png" alt="cloneX" className="h-full w-full object-contain" />
          </div>

          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-4 py-1.5 text-sm font-semibold text-red-400 backdrop-blur-sm">
            <Shield className="h-4 w-4" />
            Authorized cloning only
          </div>

          <h1 className="mx-auto max-w-4xl text-5xl font-black tracking-tight sm:text-7xl lg:text-8xl text-white text-glow">
            EXTRACT & REBUILD <br />
            <span className="gradient-text">ANY SITE YOU OWN</span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-white/60">
            cloneX crawls authorized websites, downloads assets, removes proprietary branding,
            and generates clean, editable project templates ready for redesign.
          </p>

          <div className="mt-10 flex justify-center gap-4">
            <Link href="/register">
              <Button size="lg" className="gap-2 bg-red-600 hover:bg-red-700 text-white shadow-[0_0_30px_rgba(220,38,38,0.45)]">
                Start cloning <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="border-white/10 bg-white/5 text-white hover:bg-white/10 hover:text-white">
                Sign in
              </Button>
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mx-auto mt-24 grid max-w-5xl gap-6 sm:grid-cols-2 lg:grid-cols-4"
        >
          {[
            { icon: Globe, title: 'Full crawl', desc: 'Internal links, sitemaps, and asset discovery.' },
            { icon: Zap, title: 'Clean output', desc: 'Modular project structure with local assets.' },
            { icon: Lock, title: 'Security first', desc: 'Robots.txt respect, URL validation, no credentials.' },
            { icon: Shield, title: 'Brand safe', desc: 'Automatic placeholder replacement.' },
          ].map((feature, idx) => (
            <div
              key={idx}
              className="group rounded-xl border border-white/5 bg-black/40 p-6 text-center backdrop-blur-sm transition-all hover:border-red-500/30 hover:bg-black/60"
            >
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-red-500/10 text-red-500 transition-colors group-hover:bg-red-500/20">
                <feature.icon className="h-6 w-6" />
              </div>
              <h3 className="font-bold text-white">{feature.title}</h3>
              <p className="mt-2 text-sm text-white/50">{feature.desc}</p>
            </div>
          ))}
        </motion.div>
      </main>
    </div>
  )
}
