"use client"

import { useState } from "react"
import { AuthLayout, RegisterForm, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@repo/ui"
import Link from "next/link"
import { useAuth } from "@/lib/auth-context"

export default function RegisterPage() {
  const { register } = useAuth()
  const [error, setError] = useState<string>("")

  const handleRegister = async (data: { email: string; password: string; firstName: string; lastName: string }) => {
    try {
      setError("")
      await register(data)
    } catch (err: any) {
      setError(err?.message || "Registration failed. Please try again.")
    }
  }

  return (
    <AuthLayout>
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold">Create Candidate Account</CardTitle>
        <CardDescription>
          Enter your details to create your account and start interviewing
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}
        <RegisterForm onSubmit={handleRegister} />
      </CardContent>
      <CardFooter>
        <p className="text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href="/login" className="underline underline-offset-4 hover:text-primary">
            Sign in
          </Link>
        </p>
      </CardFooter>
    </AuthLayout>
  )
}
