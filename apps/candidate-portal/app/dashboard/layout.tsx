"use client";

import { CandidateSidebar } from "@/components/candidate-sidebar"
import { DashboardLayout, Button } from "@repo/ui"
import { ProtectedRoute } from "@/components/protected-route"
import { useAuth } from "@/lib/auth-context"

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()

  return (
    <ProtectedRoute>
      <DashboardLayout 
        sidebar={<CandidateSidebar />} 
        navbar={
          <div className="ml-auto flex items-center space-x-4">
            <span className="text-sm font-medium">
              {user?.firstName || user?.email}
            </span>
            <Button variant="ghost" size="sm" onClick={logout}>
              Logout
            </Button>
          </div>
        }
      >
        {children}
      </DashboardLayout>
    </ProtectedRoute>
  )
}
