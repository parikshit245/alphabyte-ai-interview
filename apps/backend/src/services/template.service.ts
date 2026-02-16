import { db } from "@repo/database";

export class TemplateService {

    async createJob(recruiterId: string, data: { title: string; description: string }) {
        const job = await db.job.create({
            data: {
                recruiterId,
                title: data.title,
                description: data.description,
                status: "OPEN",
            },
        });
        return job;
    }

    async createTemplate(data: {
        jobId?: string;
        type: 'MOCK' | 'REAL';
        title?: string;
        createdById: string;
        questions: { text: string; order: number; type: 'TEXT' | 'CODING' }[];
    }) {
        const template = await db.interviewTemplate.create({
            data: {
                jobId: data.jobId || null,
                type: data.type,
                title: data.title || null,
                createdById: data.createdById,
                questions: {
                    create: data.questions.map((q) => ({
                        questionText: q.text,
                        order: q.order,
                        type: q.type,
                    })),
                },
            },
            include: {
                questions: true,
            },
        });
        return template;
    }

    async getJobWithTemplates(jobId: string) {
        const job = await db.job.findUnique({
            where: { id: jobId },
            include: {
                templates: {
                    include: {
                        questions: true,
                    },
                },
            },
        });
        return job;
    }

    async listJobs(recruiterId?: string) {
        const jobs = await db.job.findMany({
            where: recruiterId ? { recruiterId } : undefined,
            include: {
                templates: true,
            },
            orderBy: { createdAt: "desc" },
        });
        return jobs;
    }

    async listTemplates(type?: 'MOCK' | 'REAL') {
        const templates = await db.interviewTemplate.findMany({
            where: type ? { type } : undefined,
            include: {
                questions: true,
            },
            orderBy: { createdAt: "desc" },
        });
        return templates;
    }

    async getTemplate(templateId: string) {
        const template = await db.interviewTemplate.findUnique({
            where: { id: templateId },
            include: {
                questions: {
                    orderBy: { order: "asc" },
                },
            },
        });
        return template;
    }
}

export const templateService = new TemplateService();
