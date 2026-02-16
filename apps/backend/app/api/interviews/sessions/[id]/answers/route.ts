import { NextRequest, NextResponse } from "next/server";
import { interviewService } from "@/services/interview.service";
import { z } from "zod";

const submitAnswerSchema = z.object({
    questionId: z.string(),
    answerText: z.string(),
});

export async function POST(
    req: NextRequest,
    props: { params: Promise<{ id: string }> }
) {
    try {
        const params = await props.params;
        const sessionId = params.id;
        const body = await req.json();
        const data = submitAnswerSchema.parse(body);

        const answer = await interviewService.submitAnswer(
            sessionId,
            data.questionId,
            data.answerText
        );

        return NextResponse.json(answer);
    } catch (error) {
        console.error("Submit answer error:", error);
        return NextResponse.json(
            { error: "Failed to submit answer" },
            { status: 500 }
        );
    }
}
