"use client"

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi, User } from '@/lib/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, firstName: string, lastName: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
  updateUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const { access_token, refresh_token } = await authApi.login({ email, password })
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
          
          const user = await authApi.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (email: string, password: string, firstName: string, lastName: string) => {
        set({ isLoading: true })
        try {
          const { access_token, refresh_token } = await authApi.register({
            email,
            password,
            first_name: firstName,
            last_name: lastName,
          })
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
          
          const user = await authApi.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        authApi.logout()
        set({ user: null, isAuthenticated: false })
      },

      fetchUser: async () => {
        const token = localStorage.getItem('access_token')
        if (!token) {
          set({ isAuthenticated: false, user: null })
          return
        }

        set({ isLoading: true })
        try {
          const user = await authApi.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error) {
          set({ user: null, isAuthenticated: false, isLoading: false })
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      },

      updateUser: (user: User) => {
        set({ user })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)
