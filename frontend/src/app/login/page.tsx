"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Server, Lock, Mail, ArrowRight, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '@/store/auth'
import { toast } from '@/hooks/use-toast'

export default function LoginPage() {
  const router = useRouter()
  const login = useAuthStore((state) => state.login)
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      await login(formData.email, formData.password)
      toast({
        title: '✨ Welcome back!',
        description: 'You have been logged in successfully.',
      })
      router.push('/dashboard')
    } catch (error: any) {
      toast({
        title: '❌ Login Failed',
        description: error.response?.data?.detail || 'Invalid email or password',
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-slate-50 via-purple-50 to-blue-50 dark:from-slate-950 dark:via-purple-950 dark:to-slate-900 p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-200/30 dark:bg-purple-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-200/30 dark:bg-blue-500/10 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-600 to-blue-600 shadow-lg shadow-purple-500/50 mb-4">
            <Server className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            Uni-Manager
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-2">
            Manage your VMs with ease
          </p>
        </div>

        {/* Login Card */}
        <Card className="border-slate-200/60 dark:border-slate-800 shadow-2xl shadow-slate-900/10 dark:shadow-none backdrop-blur-sm bg-white/80 dark:bg-slate-900/80">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Welcome back</CardTitle>
            <CardDescription className="text-center">
              Sign in to your account to continue
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium">
                  Email
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="admin@unishadow.ovh"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    disabled={isLoading}
                    className="pl-10 h-11 border-slate-200 dark:border-slate-800 focus:ring-purple-500"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password" className="text-sm font-medium">
                    Password
                  </Label>
                  <Link
                    href="/forgot-password"
                    className="text-sm text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 font-medium"
                  >
                    Forgot?
                  </Link>
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                    disabled={isLoading}
                    className="pl-10 h-11 border-slate-200 dark:border-slate-800 focus:ring-purple-500"
                  />
                </div>
              </div>

              <Button
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg shadow-purple-500/50 transition-all duration-200"
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Signing in...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    Sign in
                    <ArrowRight className="w-4 h-4" />
                  </div>
                )}
              </Button>
            </form>

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200 dark:border-slate-800" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white dark:bg-slate-900 text-slate-500">
                  Don't have an account?
                </span>
              </div>
            </div>

            {/* Register Link */}
            <Link href="/register">
              <Button
                type="button"
                variant="outline"
                className="w-full h-11 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Create an account
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Footer */}
        <p className="text-center text-sm text-slate-500 mt-6">
          By signing in, you agree to our{' '}
          <a href="#" className="text-purple-600 hover:text-purple-700 dark:text-purple-400">
            Terms
          </a>{' '}
          and{' '}
          <a href="#" className="text-purple-600 hover:text-purple-700 dark:text-purple-400">
            Privacy Policy
          </a>
        </p>
      </div>
    </div>
  )
}
