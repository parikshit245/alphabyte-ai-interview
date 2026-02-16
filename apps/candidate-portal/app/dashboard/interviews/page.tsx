"use client";

import { useEffect, useState } from "react";
import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle, Table, TableHeader, TableRow, TableHead, TableBody, TableCell, Badge, Skeleton } from "@repo/ui";
import { Video } from "lucide-react";
import { api } from "@/lib/api";

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
  type?: string; // Not in DB yet, maybe mock or derive
}

export default function InterviewsPage() {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchInterviews = async () => {
      try {
        const data = await api.get<Interview[]>("/interviews");
        setInterviews(data);
      } catch (err) {
        console.error("Failed to fetch interviews:", err);
        setError("Failed to load interviews.");
      } finally {
        setLoading(false);
      }
    };

    fetchInterviews();
  }, []);

  if (loading) {
     return <InterviewsSkeleton />;
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Interview History</h1>
          <p className="text-muted-foreground">View your past and upcoming interviews.</p>
        </div>
        <Button>
          <Video className="mr-2 h-4 w-4" /> Join Meeting
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Interviews</CardTitle>
          <CardDescription>
             A list of all scheduled and completed interviews.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Company</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Date & Time</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {interviews.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center h-24 text-muted-foreground">
                    No interviews found.
                  </TableCell>
                </TableRow>
              ) : (
                interviews.map((interview) => (
                  <TableRow key={interview.id}>
                    <TableCell className="font-medium">{interview.job.company.name}</TableCell>
                    <TableCell>{interview.job.title}</TableCell>
                    <TableCell>
                       <div className="flex flex-col">
                          <span>{new Date(interview.scheduledAt).toLocaleDateString()}</span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(interview.scheduledAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                       </div>
                    </TableCell>
                    <TableCell>{interview.type || "General Interview"}</TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={`
                          ${interview.status === 'SCHEDULED' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' : ''}
                          ${interview.status === 'COMPLETED' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' : ''}
                          ${interview.status === 'CANCELLED' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' : ''}
                        `}
                      >
                        {interview.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {interview.status === 'SCHEDULED' && <Button size="sm">Join</Button>}
                      {interview.status === 'COMPLETED' && <Button size="sm" variant="outline">View Results</Button>}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

function InterviewsSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-48" />
        </div>
        <Skeleton className="h-10 w-32" />
      </div>
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-4 w-64" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

