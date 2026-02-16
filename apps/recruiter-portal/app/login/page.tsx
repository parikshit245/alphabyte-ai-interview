"use client"

import { useState } from "react"
import { AuthLayout, AuthForm, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@repo/ui"
import Link from "next/link"
import { useAuth } from "@/lib/auth-context"

export default function LoginPage() {
  const { login } = useAuth()
  const [error, setError] = useState<string>("")

  const handleLogin = async (email: string, password: string) => {
    try {
      setError("")
      await login(email, password)
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred. Please try again.")
    }
  }

  return (
    <AuthLayout>
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold">Recruiter Login</CardTitle>
        <CardDescription>
          Enter your email to sign in to your hiring dashboard
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}
        <AuthForm type="login" onSubmit={handleLogin} />
      </CardContent>
      <CardFooter>
        <p className="text-sm text-muted-foreground">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="underline underline-offset-4 hover:text-primary">
            Sign up
          </Link>
        </p>
      </CardFooter>
    </AuthLayout>
  )
}
