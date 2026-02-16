"use client"

import * as React from "react"
import { cn } from "../lib/utils"
import { Button } from "./button"
import { Input } from "./input"
import { Label } from "./label"

interface RegisterFormProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "onSubmit"> {
  onSubmit?: (data: {
    email: string
    password: string
    firstName: string
    lastName: string
  }) => void | Promise<void>
  loading?: boolean
}

export function RegisterForm({ className, onSubmit, loading: externalLoading, ...props }: RegisterFormProps) {
  const [loading, setLoading] = React.useState(false)

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    
    const formData = new FormData(e.currentTarget)
    const email = formData.get("email") as string
    const password = formData.get("password") as string
    const confirmPassword = formData.get("confirmPassword") as string
    const firstName = formData.get("firstName") as string
    const lastName = formData.get("lastName") as string
    
    if (!email || !password || !firstName || !lastName) return
    
    if (password !== confirmPassword) {
      alert("Passwords do not match")
      return
    }

    setLoading(true)
    try {
      await onSubmit?.({ email, password, firstName, lastName })
    } finally {
      setLoading(false)
    }
  }

  const isLoading = loading || externalLoading

  return (
    <div className={cn("grid gap-6", className)} {...props}>
      <form onSubmit={handleSubmit}>
        <div className="grid gap-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="firstName">First Name</Label>
              <Input
                id="firstName"
                name="firstName"
                placeholder="John"
                type="text"
                autoCapitalize="words"
                autoComplete="given-name"
                disabled={isLoading}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="lastName">Last Name</Label>
              <Input
                id="lastName"
                name="lastName"
                placeholder="Doe"
                type="text"
                autoCapitalize="words"
                autoComplete="family-name"
                disabled={isLoading}
                required
              />
            </div>
          </div>
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
              placeholder="Min. 8 characters"
              minLength={8}
              disabled={isLoading}
              required
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="confirmPassword">Confirm Password</Label>
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              placeholder="Confirm your password"
              minLength={8}
              disabled={isLoading}
              required
            />
          </div>
          <Button disabled={isLoading} type="submit">
            {isLoading && (
              <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            )}
            Create Account
          </Button>
        </div>
      </form>
    </div>
  )
}
