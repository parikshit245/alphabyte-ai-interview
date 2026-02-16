import * as React from "react"
import { Menu } from "lucide-react"
import { cn } from "../lib/utils"
import { Button } from "./button"

export function Navbar({
  className,
  children,
  onMenuClick,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & {
  onMenuClick?: () => void
}) {
  return (
    <header
      className={cn(
        "flex h-14 items-center gap-4 border-b bg-background px-6",
        className
      )}
      {...props}
    >
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden"
        onClick={onMenuClick}
      >
        <Menu className="h-5 w-5" />
        <span className="sr-only">Toggle Menu</span>
      </Button>
      {children}
    </header>
  )
}
