import * as React from "react"
import { cn } from "../lib/utils"


export function Sidebar({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "flex h-screen w-64 flex-col border-r bg-card transition-all duration-300",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function SidebarHeader({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("flex h-14 items-center border-b px-4", className)}
      {...props}
    >
      {children}
    </div>
  )
}

export function SidebarContent({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("flex-1 overflow-auto py-2", className)}
      {...props}
    >
      {children}
    </div>
  )
}

export function SidebarFooter({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("border-t p-4", className)} {...props}>
      {children}
    </div>
  )
}

export function SidebarItem({
  className,
  icon: Icon,
  children,
  active,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & {
  icon?: React.ElementType
  active?: boolean
}) {
  return (
    <div
      className={cn(
        "flex cursor-pointer items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary",
        active && "bg-muted text-primary",
        className
      )}
      {...props}
    >
      {Icon && <Icon className="h-4 w-4" />}
      <span className="text-sm font-medium">{children}</span>
    </div>
  )
}
