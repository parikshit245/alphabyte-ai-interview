"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Skeleton } from "@repo/ui";
import { Calendar, FileText, TrendingUp, ArrowRight } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";

interface DashboardStats {
  upcomingInterviews: number;
  completedInterviews: number; // mapped to applications for now or distinct
  profileViews: number;
  profileScore: number;
}

interface Interview {
  id: string;
  job: {
    title: string;
    company: {
      name: string;
    };
  };
  scheduledAt: string;
  status: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentInterviews, setRecentInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, interviewsData] = await Promise.all([
          api.get<DashboardStats>("/dashboard/stats"),
          api.get<Interview[]>("/interviews"),
        ]);
        setStats(statsData);
        setRecentInterviews(interviewsData.slice(0, 5));
      } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
        setError("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
     return <DashboardSkeleton />;
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <div className="flex items-center gap-2">
          <Link href="/dashboard/mock-interview">
            <Button>Mock Interview</Button>
          </Link>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Upcoming Interviews</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.upcomingInterviews || 0}</div>
            <p className="text-xs text-muted-foreground">Scheduled sessions</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.completedInterviews || 0}</div>
            <p className="text-xs text-muted-foreground">Past interviews</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Profile Views</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.profileViews || 0}</div>
            <p className="text-xs text-muted-foreground">Last 30 days</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Profile Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.profileScore || 0}%</div>
            <p className="text-xs text-muted-foreground">Based on performance</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest interview activities</CardDescription>
          </CardHeader>
          <CardContent>
             <div className="space-y-4">
               {recentInterviews.length === 0 ? (
                 <p className="text-sm text-muted-foreground">No recent activity.</p>
               ) : (
                 recentInterviews.map((interview) => (
                   <div key={interview.id} className="flex items-center justify-between border-b pb-4 last:border-0 last:pb-0">
                      <div>
                        <p className="font-medium">{interview.job.title}</p>
                        <p className="text-sm text-muted-foreground">
                          {interview.job.company.name} • {new Date(interview.scheduledAt).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          interview.status === 'COMPLETED' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
                          interview.status === 'SCHEDULED' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' :
                          'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                        }`}>
                          {interview.status}
                        </span>
                      </div>
                   </div>
                 ))
               )}
             </div>
          </CardContent>
        </Card>
        <Card className="col-span-3">
           <CardHeader>
             <CardTitle>Recommended Actions</CardTitle>
             <CardDescription>Improve your chances</CardDescription>
           </CardHeader>
           <CardContent className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border p-4">
                 <div>
                   <p className="font-medium">Update Resume</p>
                   <p className="text-sm text-muted-foreground">Keep your profile fresh</p>
                 </div>
                 <Button size="sm" variant="outline"><ArrowRight className="h-4 w-4" /></Button>
              </div>
              <div className="flex items-center justify-between rounded-lg border p-4">
                 <div>
                   <p className="font-medium">Take Mock Interview</p>
                   <p className="text-sm text-muted-foreground">Practice makes perfect</p>
                 </div>
                 <Link href="/dashboard/mock-interview">
                    <Button size="sm" variant="outline"><ArrowRight className="h-4 w-4" /></Button>
                 </Link>
              </div>
           </CardContent>
        </Card>
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <Skeleton className="h-10 w-40" />
        <Skeleton className="h-10 w-32" />
      </div>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        <Skeleton className="col-span-4 h-64" />
        <Skeleton className="col-span-3 h-64" />
      </div>
    </div>
  );
}

