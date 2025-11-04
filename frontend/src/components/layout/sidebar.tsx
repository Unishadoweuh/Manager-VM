"use client"

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/store/auth'
import {
  LayoutDashboard,
  Server,
  Box,
  CreditCard,
  Activity,
  FileText,
  Settings,
  Users,
  Database,
} from 'lucide-react'

interface NavItem {
  title: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  adminOnly?: boolean
}

const navItems: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    title: 'Virtual Machines',
    href: '/vms',
    icon: Server,
  },
  {
    title: 'Templates',
    href: '/templates',
    icon: Box,
  },
  {
    title: 'Credits',
    href: '/credits',
    icon: CreditCard,
  },
  {
    title: 'Monitoring',
    href: '/monitoring',
    icon: Activity,
  },
  {
    title: 'Audit Logs',
    href: '/logs',
    icon: FileText,
  },
]

const adminNavItems: NavItem[] = [
  {
    title: 'Users',
    href: '/admin/users',
    icon: Users,
    adminOnly: true,
  },
  {
    title: 'Servers',
    href: '/admin/servers',
    icon: Database,
    adminOnly: true,
  },
  {
    title: 'Templates',
    href: '/admin/templates',
    icon: Box,
    adminOnly: true,
  },
  {
    title: 'Admin Logs',
    href: '/admin/logs',
    icon: FileText,
    adminOnly: true,
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const user = useAuthStore((state) => state.user)
  const isAdmin = user?.role === 'admin'

  const items = isAdmin ? [...navItems, ...adminNavItems] : navItems

  return (
    <div className="flex h-screen w-64 flex-col border-r bg-card">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Server className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-xl font-bold">Uni-Manager</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {items.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <Icon className="h-5 w-5" />
              {item.title}
            </Link>
          )
        })}
      </nav>

      {/* User Info */}
      <div className="border-t p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
            {user?.first_name?.[0]}{user?.last_name?.[0]}
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="truncate text-sm font-medium">
              {user?.first_name} {user?.last_name}
            </p>
            <p className="truncate text-xs text-muted-foreground">{user?.email}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
