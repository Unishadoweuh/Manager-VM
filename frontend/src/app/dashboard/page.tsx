"use client"

import { useEffect, useState } from 'react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { useAuthStore } from '@/store/auth'
import { vmApi, userApi, VM, Transaction } from '@/lib/api'
import { formatCurrency, formatRelativeTime } from '@/lib/utils'
import { Server, CreditCard, Activity, Plus, Play, Square } from 'lucide-react'
import Link from 'next/link'

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user)
  const [vms, setVms] = useState<VM[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [vmsData, transactionsData] = await Promise.all([
          vmApi.getAll(),
          userApi.getTransactions(),
        ])
        setVms(vmsData)
        setTransactions(transactionsData.slice(0, 5)) // Last 5 transactions
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  const runningVMs = vms.filter((vm) => vm.state === 'running').length
  const totalVMs = vms.length
  const totalCost = vms.reduce((sum, vm) => sum + parseFloat(vm.total_cost), 0)

  const getVMStateBadge = (state: VM['state']) => {
    const variants: Record<VM['state'], 'success' | 'warning' | 'destructive' | 'secondary' | 'default'> = {
      running: 'success',
      stopped: 'secondary',
      creating: 'warning',
      suspended: 'warning',
      error: 'destructive',
      deleting: 'warning',
      deleted: 'destructive',
    }
    return <Badge variant={variants[state]}>{state}</Badge>
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">
              Welcome back, {user?.first_name}!
            </p>
          </div>
          <Link href="/vms">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create VM
            </Button>
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Balance</CardTitle>
              <CreditCard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(user?.balance || '0')}</div>
              <p className="text-xs text-muted-foreground">
                <Link href="/credits" className="text-primary hover:underline">
                  Add credits
                </Link>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Virtual Machines</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalVMs}</div>
              <p className="text-xs text-muted-foreground">
                {runningVMs} running
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Usage</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(totalCost)}</div>
              <p className="text-xs text-muted-foreground">
                All-time costs
              </p>
            </CardContent>
          </Card>
        </div>

        {/* VMs List */}
        <Card>
          <CardHeader>
            <CardTitle>Your Virtual Machines</CardTitle>
            <CardDescription>
              {totalVMs > 0 ? `You have ${totalVMs} virtual machine${totalVMs > 1 ? 's' : ''}` : 'No virtual machines yet'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : totalVMs === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Server className="h-12 w-12 text-muted-foreground" />
                <h3 className="mt-4 text-lg font-semibold">No VMs found</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  Get started by creating your first virtual machine
                </p>
                <Link href="/vms">
                  <Button className="mt-4">
                    <Plus className="mr-2 h-4 w-4" />
                    Create VM
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {vms.slice(0, 5).map((vm) => (
                  <div
                    key={vm.id}
                    className="flex items-center justify-between rounded-lg border p-4 hover:bg-accent"
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                        <Server className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">{vm.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {vm.cpu_cores} vCPU • {vm.ram_mb / 1024}GB RAM • {vm.disk_gb}GB Disk
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {getVMStateBadge(vm.state)}
                      <Link href={`/vms/${vm.id}`}>
                        <Button variant="outline" size="sm">
                          Manage
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
                {totalVMs > 5 && (
                  <Link href="/vms">
                    <Button variant="outline" className="w-full">
                      View all VMs
                    </Button>
                  </Link>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Transactions */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Transactions</CardTitle>
            <CardDescription>Your latest credit transactions</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : transactions.length === 0 ? (
              <p className="text-center text-sm text-muted-foreground">No transactions yet</p>
            ) : (
              <div className="space-y-3">
                {transactions.map((transaction) => (
                  <div
                    key={transaction.id}
                    className="flex items-center justify-between rounded-lg border p-3"
                  >
                    <div>
                      <p className="text-sm font-medium">{transaction.description}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatRelativeTime(transaction.created_at)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className={`text-sm font-semibold ${
                        parseFloat(transaction.amount) >= 0 ? 'text-green-600' : 'text-destructive'
                      }`}>
                        {parseFloat(transaction.amount) >= 0 ? '+' : ''}{formatCurrency(transaction.amount)}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Balance: {formatCurrency(transaction.balance_after)}
                      </p>
                    </div>
                  </div>
                ))}
                <Link href="/credits">
                  <Button variant="outline" className="w-full">
                    View all transactions
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
