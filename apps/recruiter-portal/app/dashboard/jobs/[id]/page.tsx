"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle, Input, Label, Textarea, Badge, Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@repo/ui";
import { Plus, Trash2, ArrowLeft } from "lucide-react";
import { api } from "@/lib/api";

type Job = {
  id: string;
  title: string;
  description: string;
  status: string;
  templates: Template[];
};

type Template = {
  id: string;
  title?: string;
  type: string;
  questions: Question[];
  createdAt: string;
};

type Question = {
  text: string;
  order: number;
  type: "TEXT" | "CODING";
};

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.id as string;

  const [job, setJob] = useState<Job | null>(null);
  const [showDialog, setShowDialog] = useState(false);
  const [templateForm, setTemplateForm] = useState({
    title: "",
    type: "REAL" as "MOCK" | "REAL",
  });
  const [questions, setQuestions] = useState<Question[]>([
    { text: "", order: 1, type: "TEXT" }
  ]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (jobId) {
      fetchJob();
    }
  }, [jobId]);

  const fetchJob = async () => {
    try {
      const data = await api.get<Job>(`/jobs/${jobId}`);
      setJob(data);
    } catch (e) {
      console.error("Failed to fetch job", e);
      alert("Failed to load job");
    }
  };

  const handleAddQuestion = () => {
    setQuestions([
      ...questions,
      { text: "", order: questions.length + 1, type: "TEXT" }
    ]);
  };

  const handleRemoveQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index));
  };

  const handleQuestionChange = (index: number, field: keyof Question, value: string | number) => {
    const updated = [...questions];
    updated[index] = { ...updated[index], [field]: value } as Question;
    setQuestions(updated);
  };

  const handleCreateTemplate = async (e: React.FormEvent) => {
    e.preventDefault();
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    if (!user.id) {
      alert("Please login first");
      return;
    }

    if (questions.some(q => !q.text.trim())) {
      alert("All questions must have text");
      return;
    }

    setLoading(true);
    try {
      await api.post("/templates", {
        jobId: jobId,
        type: templateForm.type,
        title: templateForm.title || undefined,
        createdById: user.id,
        questions: questions.map(q => ({ ...q, text: q.text.trim() })),
      });

      setTemplateForm({ title: "", type: "REAL" });
      setQuestions([{ text: "", order: 1, type: "TEXT" }]);
      setShowDialog(false);
      await fetchJob();
    } catch (e) {
      console.error("Failed to create template", e);
      alert("Failed to create template");
    } finally {
      setLoading(false);
    }
  };

  if (!job) {
    return (
      <div className="space-y-6">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => router.push("/dashboard/jobs")}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-2xl">{job.title}</CardTitle>
              <CardDescription className="mt-2">{job.description}</CardDescription>
            </div>
            <Badge>{job.status}</Badge>
          </div>
        </CardHeader>
      </Card>

      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Interview Templates</h2>
        
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" /> Create Template
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create Interview Template</DialogTitle>
              <DialogDescription>
                Add questions for this interview template
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreateTemplate} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">Template Title (Optional)</Label>
                <Input
                  id="title"
                  value={templateForm.title}
                  onChange={(e) => setTemplateForm({ ...templateForm, title: e.target.value })}
                  placeholder="e.g., Technical Screen"
                />
              </div>

              <div className="space-y-2">
                <Label>Questions</Label>
                {questions.map((question, index) => (
                  <Card key={index} className="p-4">
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <Label>Question {index + 1}</Label>
                        {questions.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveQuestion(index)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                      <Textarea
                        value={question.text}
                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleQuestionChange(index, "text", e.target.value)}
                        placeholder="Enter your question..."
                        rows={3}
                        required
                      />
                      <div className="flex gap-2">
                        <Label className="text-sm text-muted-foreground">Type:</Label>
                        <select
                          value={question.type}
                          onChange={(e) => handleQuestionChange(index, "type", e.target.value)}
                          className="text-sm border rounded px-2 py-1"
                        >
                          <option value="TEXT">Text</option>
                          <option value="CODING">Coding</option>
                        </select>
                      </div>
                    </div>
                  </Card>
                ))}
                <Button type="button" variant="outline" onClick={handleAddQuestion} className="w-full">
                  <Plus className="h-4 w-4 mr-2" /> Add Question
                </Button>
              </div>

              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={() => setShowDialog(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={loading}>
                  {loading ? "Creating..." : "Create Template"}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {job.templates.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">
              No templates created yet. Click "Create Template" to add interview questions.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {job.templates.map((template) => (
            <Card key={template.id}>
              <CardHeader>
                <CardTitle className="text-lg">
                  {template.title || "Interview Template"}
                </CardTitle>
                <CardDescription>
                  {template.type === "MOCK" ? "Mock Interview" : "Real Interview"}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-sm text-muted-foreground">
                  {template.questions.length} questions
                </p>
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => router.push(`/dashboard/interviews?templateId=${template.id}`)}
                >
                  View Sessions
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
