import { NextRequest, NextResponse } from "next/server";
import { templateService } from "@/services/template.service";
import { z } from "zod";

const createJobSchema = z.object({
    recruiterId: z.string(),
    title: z.string(),
    description: z.string(),
});

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const data = createJobSchema.parse(body);

        const job = await templateService.createJob(data.recruiterId, {
            title: data.title,
            description: data.description,
        });

        return NextResponse.json(job);
    } catch (error) {
        console.error("Create job error:", error);
        return NextResponse.json(
            { error: "Failed to create job" },
            { status: 500 }
        );
    }
}

export async function GET(req: NextRequest) {
    try {
        const recruiterId = req.nextUrl.searchParams.get("recruiterId") || undefined;
        const jobs = await templateService.listJobs(recruiterId);
        return NextResponse.json(jobs);
    } catch (error) {
        console.error("List jobs error:", error);
        return NextResponse.json({ error: "Failed to list jobs" }, { status: 500 });
    }
}
