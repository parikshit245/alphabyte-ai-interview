"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Card, CardContent, Table, TableHeader, TableRow, TableHead, TableBody, TableCell, Badge } from "@repo/ui";
import { Eye } from "lucide-react";
import { api } from "@/lib/api";

type Session = {
  id: string;
  status: string;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  candidate: {
    id: string;
    firstName: string;
    lastName: string;
    email: string;
  };
  resume: {
    id: string;
    fileName: string;
  };
  template: {
    job: {
      id: string;
      title: string;
    };
    questions: any[];
  };
  answers: any[];
};

export default function InterviewsPage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    if (!user.id) return;

    setLoading(true);
    try {
      const data = await api.get<Session[]>(`/recruiter/sessions?recruiterId=${user.id}`);
      setSessions(data);
    } catch (e) {
      console.error("Failed to fetch sessions", e);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "outline"> = {
      CREATED: "outline",
      IN_PROGRESS: "default",
      COMPLETED: "secondary",
    };
    return <Badge variant={variants[status] || "outline"}>{status}</Badge>;
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Interview Sessions</h1>
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">Loading sessions...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Interview Sessions</h1>
        <p className="text-muted-foreground">Review candidate interview responses</p>
      </div>

      {sessions.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">
              No interview sessions yet. Candidates will appear here after starting interviews.
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Candidate</TableHead>
                  <TableHead>Job</TableHead>
                  <TableHead>Questions</TableHead>
                  <TableHead>Answered</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Started</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sessions.map((session) => (
                  <TableRow key={session.id}>
                    <TableCell className="font-medium">
                      {session.candidate.firstName} {session.candidate.lastName}
                      <div className="text-xs text-muted-foreground">{session.candidate.email}</div>
                    </TableCell>
                    <TableCell>{session.template.job?.title || "N/A"}</TableCell>
                    <TableCell>{session.template.questions.length}</TableCell>
                    <TableCell>{session.answers.length}</TableCell>
                    <TableCell>{getStatusBadge(session.status)}</TableCell>
                    <TableCell>
                      {session.startedAt
                        ? new Date(session.startedAt).toLocaleDateString()
                        : "Not started"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => router.push(`/dashboard/interviews/${session.id}`)}
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        Review
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
