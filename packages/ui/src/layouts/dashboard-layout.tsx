"use client"

import * as React from "react"
import { Navbar } from "../components/navbar"


// Interface
interface DashboardLayoutProps {
  children: React.ReactNode
  sidebar: React.ReactNode
  navbar?: React.ReactNode
}

export function DashboardLayout({
  children,
  sidebar,
  navbar,
}: DashboardLayoutProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Desktop Sidebar */}
      <aside className="hidden w-64 flex-col border-r bg-card md:flex">
        {sidebar}
      </aside>

      {/* Mobile Sidebar Overlay (Simple implementation without Sheet for now to avoid dependency hell if Sheet missing) */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <div 
             className="fixed inset-0 bg-black/80" 
             onClick={() => setIsMobileMenuOpen(false)}
          />
          <div className="relative flex w-64 flex-col bg-card animate-in slide-in-from-left">
            {sidebar}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar onMenuClick={() => setIsMobileMenuOpen(true)}>
          {navbar}
        </Navbar>
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
