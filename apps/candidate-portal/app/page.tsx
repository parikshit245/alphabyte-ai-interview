import Link from "next/link";
import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from "@repo/ui";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-6 text-gray-900 dark:text-white">
            AI Interview Platform
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-12">
            Welcome to the Candidate Portal. Prepare for AI-powered interviews and showcase your
            skills.
          </p>

          <div className="grid md:grid-cols-2 gap-6 mb-12">
            <Card>
              <CardHeader>
                <CardTitle>Dashboard</CardTitle>
                <CardDescription>View your upcoming interviews</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href="/dashboard">
                  <Button className="w-full">Go to Dashboard</Button>
                </Link>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>My Interviews</CardTitle>
                <CardDescription>Track your interview progress</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href="/interviews">
                  <Button variant="outline" className="w-full">
                    View Interviews
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>

          <div className="text-sm text-gray-500 dark:text-gray-400">
            <p>Candidate Portal is running on port 3000</p>
            <p className="mt-2">Backend API: http://localhost:3003</p>
          </div>
        </div>
      </div>
    </div>
  );
}
