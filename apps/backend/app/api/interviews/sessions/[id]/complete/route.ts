import { NextRequest, NextResponse } from "next/server";
import { interviewService } from "@/services/interview.service";

export async function POST(
    _req: NextRequest,
    props: { params: Promise<{ id: string }> }
) {
    try {
        const params = await props.params;
        const sessionId = params.id;
        const session = await interviewService.completeSession(sessionId);

        return NextResponse.json(session);
    } catch (error) {
        console.error("Complete session error:", error);
        return NextResponse.json(
            { error: "Failed to complete session" },
            { status: 500 }
        );
    }
}
