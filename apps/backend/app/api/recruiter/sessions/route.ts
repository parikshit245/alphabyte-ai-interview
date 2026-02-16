import { NextRequest, NextResponse } from "next/server";
import { interviewService } from "@/services/interview.service";

export async function GET(req: NextRequest) {
    try {
        const recruiterId = req.nextUrl.searchParams.get("recruiterId");

        if (!recruiterId) {
            return NextResponse.json(
                { error: "recruiterId is required" },
                { status: 400 }
            );
        }

        const sessions = await interviewService.getRecruiterSessions(recruiterId);
        return NextResponse.json(sessions);
    } catch (error) {
        console.error("Get recruiter sessions error:", error);
        return NextResponse.json(
            { error: "Failed to fetch sessions" },
            { status: 500 }
        );
    }
}
