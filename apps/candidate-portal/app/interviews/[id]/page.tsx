"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle, Textarea } from "@repo/ui";
import { api } from "@/lib/api";
import { ChevronLeft, ChevronRight, CheckCircle } from "lucide-react";

type Question = {
  id: string;
  questionText: string;
  order: number;
  type: string;
};

type Answer = {
  id: string;
  questionId: string;
  answerText: string;
};

type Session = {
  id: string;
  status: string;
  template: {
    title?: string;
    job?: {
      title: string;
    };
    questions: Question[];
  };
  answers: Answer[];
};

export default function InterviewSessionPage() {
  const router = useRouter();
  const params = useParams();
  const sessionId = params.id as string;

  const [session, setSession] = useState<Session | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (sessionId) {
      fetchSession();
    }
  }, [sessionId]);

  useEffect(() => {
    if (session && session.template.questions[currentQuestionIndex]) {
      const question = session.template.questions[currentQuestionIndex];
      const existingAnswer = session.answers.find(a => a.questionId === question.id);
      setCurrentAnswer(existingAnswer?.answerText || "");
    }
  }, [currentQuestionIndex, session]);

  const fetchSession = async () => {
    setLoading(true);
    try {
      const data = await api.get<Session>(`/interviews/sessions/${sessionId}`);
      setSession(data);
      
      // Start the session if not started
      if (data.status === "CREATED") {
        await api.post(`/interviews/sessions/${sessionId}/start`, {});
      }
    } catch (e) {
      console.error("Failed to fetch session", e);
      alert("Failed to load interview session");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAnswer = async () => {
    if (!session) return;

    const question = session.template.questions[currentQuestionIndex];
    if (!question) return;
    
    setSaving(true);
    try {
      await api.post(`/interviews/sessions/${sessionId}/answers`, {
        questionId: question.id,
        answerText: currentAnswer,
      });
      
      // Refresh session to get updated answers
      await fetchSession();
    } catch (e) {
      console.error("Failed to save answer", e);
      alert("Failed to save answer");
    } finally {
      setSaving(false);
    }
  };

  const handleNext = async () => {
    await handleSaveAnswer();
    if (session && currentQuestionIndex < session.template.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleComplete = async () => {
    await handleSaveAnswer();
    
    try {
      await api.post(`/interviews/sessions/${sessionId}/complete`, {});
      alert("Interview completed successfully!");
      router.push("/dashboard/interviews");
    } catch (e) {
      console.error("Failed to complete interview", e);
      alert("Failed to complete interview");
    }
  };

  if (loading || !session) {
    return (
      <div className="container mx-auto p-8">
        <Card>
          <CardContent className="pt-6">
            <p className="text-center">Loading interview...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentQuestion = session.template.questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === session.template.questions.length - 1;

  if (!currentQuestion) {
    return (
      <div className="container mx-auto p-8">
        <Card>
          <CardContent className="pt-6">
            <p className="text-center">Invalid question.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">
          {session.template.job?.title || session.template.title || "Interview Session"}
        </h1>
        <p className="text-muted-foreground">
          Question {currentQuestionIndex + 1} of {session.template.questions.length}
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl">
            {currentQuestion.questionText}
          </CardTitle>
          <CardDescription>
            {currentQuestion.type === "CODING" ? "Coding Question" : "Text Question"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Type your answer here..."
            value={currentAnswer}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setCurrentAnswer(e.target.value)}
            rows={12}
            className="font-mono"
          />

          <div className="flex justify-between items-center pt-4">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0}
            >
              <ChevronLeft className="mr-2 h-4 w-4" />
              Previous
            </Button>

            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={handleSaveAnswer}
                disabled={saving}
              >
                {saving ? "Saving..." : "Save"}
              </Button>

              {!isLastQuestion ? (
                <Button onClick={handleNext} disabled={saving}>
                  Next
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button onClick={handleComplete} disabled={saving}>
                  Complete Interview
                  <CheckCircle className="ml-2 h-4 w-4" />
                </Button>
              )}
            </div>
          </div>

          {/* Progress dots */}
          <div className="flex justify-center gap-2 pt-4">
            {session.template.questions.map((q, idx) => {
              const hasAnswer = session.answers.some(
                a => a.questionId === q?.id
              );
              return (
                <div
                  key={idx}
                  className={`h-2 w-2 rounded-full ${
                    idx === currentQuestionIndex
                      ? "bg-primary"
                      : hasAnswer
                      ? "bg-green-500"
                      : "bg-gray-300"
                  }`}
                />
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
