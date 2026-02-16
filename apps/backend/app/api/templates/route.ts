import { NextRequest, NextResponse } from "next/server";
import { templateService } from "@/services/template.service";
import { z } from "zod";

const createTemplateSchema = z.object({
    jobId: z.string().optional(),
    type: z.enum(['MOCK', 'REAL']),
    title: z.string().optional(),
    createdById: z.string(),
    questions: z.array(z.object({
        text: z.string(),
        order: z.number(),
        type: z.enum(['TEXT', 'CODING']),
    })),
});

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const data = createTemplateSchema.parse(body);

        const template = await templateService.createTemplate(data);

        return NextResponse.json(template);
    } catch (error) {
        console.error("Create template error:", error);
        return NextResponse.json(
            { error: "Failed to create template" },
            { status: 500 }
        );
    }
}

export async function GET(req: NextRequest) {
    try {
        const typeParam = req.nextUrl.searchParams.get("type");
        const type = (typeParam === 'MOCK' || typeParam === 'REAL') ? typeParam : undefined;

        const templates = await templateService.listTemplates(type);
        return NextResponse.json(templates);
    } catch (error) {
        console.error("List templates error:", error);
        return NextResponse.json({ error: "Failed to list templates" }, { status: 500 });
    }
}
