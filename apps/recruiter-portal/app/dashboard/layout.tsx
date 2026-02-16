"use client";

import { RecruiterSidebar } from "@/components/recruiter-sidebar"
import { DashboardLayout } from "@repo/ui"
import { ProtectedRoute } from "@/components/protected-route"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@repo/ui"

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  
  return (
    <ProtectedRoute>
      <DashboardLayout 
        sidebar={<RecruiterSidebar />} 
        navbar={
          <div className="ml-auto flex items-center space-x-4">
            <span className="text-sm font-medium">
              {user?.firstName || user?.email}
            </span>
            <Button variant="outline" size="sm" onClick={logout}>
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
