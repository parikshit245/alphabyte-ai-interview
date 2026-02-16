"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from "@repo/ui";
import { api } from "@/lib/api";

type Template = {
  id: string;
  title?: string;
  type: string;
  job?: {
    id: string;
    title: string;
  };
  questions: any[];
  createdAt: string;
};

type Resume = {
  id: string;
  fileName: string;
};

export default function OpportunitiesPage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTemplates();
    fetchResumes();
  }, []);

  const fetchTemplates = async () => {
    try {
      const data = await api.get<Template[]>("/templates");
      setTemplates(data);
    } catch (e) {
      console.error("Failed to fetch templates", e);
    }
  };

  const fetchResumes = async () => {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    if (!user.id) return;
    try {
      const data = await api.get<Resume[]>(`/resumes?userId=${user.id}`);
      setResumes(data);
    } catch (e) {
      console.error("Failed to fetch resumes", e);
    }
  };

  const handleStartInterview = async (templateId: string) => {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    if (!user.id) {
      alert("Please login first");
      return;
    }

    if (resumes.length === 0) {
      alert("Please upload a resume first");
      router.push("/dashboard/resumes");
      return;
    }

    setLoading(true);
    try {
      const session = await api.post<any>("/interviews/sessions", {
        candidateId: user.id,
        templateId: templateId,
        resumeId: resumes[0]?.id || null,
      });

      router.push(`/interviews/${session.id}`);
    } catch (err) {
      console.error("Failed to start session", err);
      alert("Failed to start interview session");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Interview Opportunities</h1>
        <p className="text-muted-foreground">Browse and start available interview sessions</p>
      </div>

      {resumes.length === 0 && (
        <Card className="border-yellow-500 bg-yellow-50 dark:bg-yellow-950">
          <CardContent className="pt-6">
            <p className="text-yellow-800 dark:text-yellow-200">
              You need to upload a resume before starting an interview.{" "}
              <Button
                variant="link"
                className="p-0 h-auto text-yellow-900 dark:text-yellow-100"
                onClick={() => router.push("/dashboard/resumes")}
              >
                Upload Resume
              </Button>
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {templates.map((template) => (
          <Card key={template.id}>
            <CardHeader>
              <CardTitle>
                {template.job?.title || template.title || "Interview Template"}
              </CardTitle>
              <CardDescription>
                {template.type === "MOCK" ? "Mock Interview" : "Real Interview"}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-sm text-muted-foreground">
                <p>{template.questions.length} questions</p>
              </div>
              <Button
                className="w-full"
                onClick={() => handleStartInterview(template.id)}
                disabled={loading || resumes.length === 0}
              >
                {loading ? "Starting..." : "Start Interview"}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {templates.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">
              No interview opportunities available at this time.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
