import { NextRequest, NextResponse } from "next/server";
import { templateService } from "@/services/template.service";

export async function GET(
    _req: NextRequest,
    props: { params: Promise<{ id: string }> }
) {
    try {
        const params = await props.params;
        const jobId = params.id;
        const job = await templateService.getJobWithTemplates(jobId);

        if (!job) {
            return NextResponse.json(
                { error: "Job not found" },
                { status: 404 }
            );
        }

        return NextResponse.json(job);
    } catch (error) {
        console.error("Get job error:", error);
        return NextResponse.json(
            { error: "Failed to fetch job" },
            { status: 500 }
        );
    }
}
