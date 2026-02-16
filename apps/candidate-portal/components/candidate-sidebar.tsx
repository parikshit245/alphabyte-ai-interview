"use client"

import { Home, FileText, Calendar, Briefcase, User, PenTool } from "lucide-react"
import { usePathname } from "next/navigation"
import Link from "next/link"
import {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarItem,
} from "@repo/ui"

export function CandidateSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar>
      <SidebarHeader>
        <span className="text-lg font-bold">Candidate Portal</span>
      </SidebarHeader>
      <SidebarContent>
        <Link href="/dashboard">
          <SidebarItem icon={Home} active={pathname === "/dashboard"}>
            Dashboard
          </SidebarItem>
        </Link>
        <Link href="/dashboard/resumes">
          <SidebarItem icon={FileText} active={pathname === "/dashboard/resumes"}>
            Resumes
          </SidebarItem>
        </Link>
        <Link href="/dashboard/interviews">
          <SidebarItem icon={Calendar} active={pathname === "/dashboard/interviews"}>
            Interviews
          </SidebarItem>
        </Link>
        <Link href="/dashboard/mock-interview">
          <SidebarItem icon={PenTool} active={pathname === "/dashboard/mock-interview"}>
            Mock Interview
          </SidebarItem>
        </Link>
        <Link href="/dashboard/opportunities">
          <SidebarItem icon={Briefcase} active={pathname === "/dashboard/opportunities"}>
            Opportunities
          </SidebarItem>
        </Link>
        <Link href="/dashboard/profile">
          <SidebarItem icon={User} active={pathname === "/dashboard/profile"}>
            Profile
          </SidebarItem>
        </Link>
      </SidebarContent>
      <SidebarFooter>
        <div className="flex items-center gap-3 px-3 py-2">
           <div className="h-8 w-8 rounded-full bg-muted"></div>
           <div className="flex flex-col">
             <span className="text-sm font-medium">Candidate User</span>
             <span className="text-xs text-muted-foreground">Free Plan</span>
           </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
