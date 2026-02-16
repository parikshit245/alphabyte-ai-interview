import Link from "next/link";
import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from "@repo/ui";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-6 text-gray-900 dark:text-white">
            Recruiter Portal
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-12">
            Manage candidates, conduct interviews, and analyze results with AI-powered insights.
          </p>

          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <Card>
              <CardHeader>
                <CardTitle>Dashboard</CardTitle>
                <CardDescription>Overview and analytics</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href="/dashboard">
                  <Button className="w-full">Go to Dashboard</Button>
                </Link>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Candidates</CardTitle>
                <CardDescription>Manage candidate pipeline</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href="/candidates">
                  <Button variant="outline" className="w-full">
                    View Candidates
                  </Button>
                </Link>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Analytics</CardTitle>
                <CardDescription>Performance insights</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href="/analytics">
                  <Button variant="outline" className="w-full">
                    View Analytics
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>

          <div className="text-sm text-gray-500 dark:text-gray-400">
            <p>Recruiter Portal is running on port 3001</p>
            <p className="mt-2">Backend API: http://localhost:3003</p>
          </div>
        </div>
      </div>
    </div>
  );
}
