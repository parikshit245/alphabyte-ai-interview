"use client"

import { Home, Users, BarChart, Settings, Briefcase, Calendar } from "lucide-react"
import { usePathname } from "next/navigation"
import Link from "next/link"
import {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarItem,
} from "@repo/ui"

export function RecruiterSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar>
      <SidebarHeader>
        <span className="text-lg font-bold">Recruiter Portal</span>
      </SidebarHeader>
      <SidebarContent>
        <Link href="/dashboard">
          <SidebarItem icon={Home} active={pathname === "/dashboard"}>
            Dashboard
          </SidebarItem>
        </Link>
        <Link href="/dashboard/jobs">
          <SidebarItem icon={Briefcase} active={pathname === "/dashboard/jobs"}>
            Jobs
          </SidebarItem>
        </Link>
        <Link href="/dashboard/candidates">
          <SidebarItem icon={Users} active={pathname === "/dashboard/candidates"}>
            Candidates
          </SidebarItem>
        </Link>
        <Link href="/dashboard/interviews">
          <SidebarItem icon={Calendar} active={pathname === "/dashboard/interviews"}>
            Interviews
          </SidebarItem>
        </Link>
        <Link href="/dashboard/analytics">
          <SidebarItem icon={BarChart} active={pathname === "/dashboard/analytics"}>
            Analytics
          </SidebarItem>
        </Link>
        <Link href="/dashboard/settings">
          <SidebarItem icon={Settings} active={pathname === "/dashboard/settings"}>
            Settings
          </SidebarItem>
        </Link>
      </SidebarContent>
      <SidebarFooter>
         <div className="flex items-center gap-3 px-3 py-2">
           <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">R</div>
           <div className="flex flex-col">
             <span className="text-sm font-medium">Recruiter Admin</span>
             <span className="text-xs text-muted-foreground">Enterprise</span>
           </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
