import { NextRequest, NextResponse } from "next/server";
import { resumeService } from "@/services/resume.service";

export async function POST(req: NextRequest) {
    try {
        const formData = await req.formData();
        const file = formData.get("file") as File | null;
        const userId = formData.get("userId") as string | null;

        if (!file || !userId) {
            return NextResponse.json(
                { error: "File and userId are required" },
                { status: 400 }
            );
        }

        const resume = await resumeService.uploadResume(userId, file);
        return NextResponse.json(resume);
    } catch (error) {
        console.error("Resume upload error:", error);
        return NextResponse.json(
            { error: "Failed to upload resume" },
            { status: 500 }
        );
    }
}

export async function GET(req: NextRequest) {
    const searchParams = req.nextUrl.searchParams;
    const userId = searchParams.get("userId");

    if (!userId) {
        return NextResponse.json({ error: "UserId required" }, { status: 400 });
    }

    try {
        const resumes = await resumeService.getResumesByUser(userId);
        return NextResponse.json(resumes);
    } catch (error) {
        console.error("Failed to fetch resumes:", error);
        return NextResponse.json({ error: "Failed to fetch resumes" }, { status: 500 });
    }
}
