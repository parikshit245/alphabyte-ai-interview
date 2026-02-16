"use client"

import * as React from "react"
import { cn } from "../lib/utils"
import { Button } from "./button"
import { Input } from "./input"
import { Label } from "./label"

interface AuthFormProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "onSubmit"> {
  type: "login" | "register"
  onSubmit?: (email: string, password: string) => void | Promise<void>
  loading?: boolean
}

export function AuthForm({ className, type, onSubmit, loading: externalLoading, ...props }: AuthFormProps) {
  const [loading, setLoading] = React.useState(false)

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    
    const formData = new FormData(e.currentTarget)
    const email = formData.get("email") as string
    const password = formData.get("password") as string
    
    if (!email || !password) return

    setLoading(true)
    try {
      await onSubmit?.(email, password)
    } finally {
      setLoading(false)
    }
  }

  const isLoading = loading || externalLoading

  return (
    <div className={cn("grid gap-6", className)} {...props}>
      <form onSubmit={handleSubmit}>
        <div className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              name="email"
              placeholder="name@example.com"
              type="email"
              autoCapitalize="none"
              autoComplete="email"
              autoCorrect="off"
              disabled={isLoading}
              required
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              name="password"
              type="password"
              disabled={isLoading}
              required
            />
          </div>
          <Button disabled={isLoading} type="submit">
            {isLoading && (
              <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            )}
            {type === "login" ? "Sign In" : "Create Account"}
          </Button>
        </div>
      </form>
    </div>
  )
}
