import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'cloneX - Website Template Extractor',
  description: 'Enterprise-grade website template extraction for authorized redesign projects.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  )
}
