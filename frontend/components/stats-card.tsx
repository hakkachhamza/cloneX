'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LucideIcon } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string | number
  description?: string
  icon: LucideIcon
  trend?: string
}

export function StatsCard({ title, value, description, icon: Icon, trend }: StatsCardProps) {
  return (
    <Card className="gradient-border">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-white/50">{title}</CardTitle>
        <div className="rounded-lg bg-red-500/10 p-2 text-red-500">
          <Icon className="h-4 w-4" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-white">{value}</div>
        {(description || trend) && (
          <p className="mt-1 text-xs text-white/40">
            {trend && <span className="mr-2 text-red-400">{trend}</span>}
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  )
}
