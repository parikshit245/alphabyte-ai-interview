import { PrismaClient } from "@repo/database";
import type { InterviewSession } from "@prisma/client";

const prisma = new PrismaClient();

export class InterviewRepository {
  async findById(id: string): Promise<InterviewSession | null> {
    return prisma.interviewSession.findUnique({
      where: { id },
      include: {
        candidate: true,
        template: {
          include: {
            job: true,
            questions: true
          }
        },
        resume: true,
        answers: true,
      },
    });
  }

  async create(data: {
    candidateId: string;
    templateId: string;
    resumeId?: string;
  }): Promise<InterviewSession> {
    return prisma.interviewSession.create({
      data: {
        ...data,
        status: 'CREATED'
      },
      include: {
        candidate: true,
        template: {
          include: {
            job: true,
            questions: true
          }
        },
        resume: true,
      },
    });
  }

  async update(id: string, data: Partial<InterviewSession>): Promise<InterviewSession> {
    return prisma.interviewSession.update({
      where: { id },
      data,
      include: {
        candidate: true,
        template: true,
        resume: true,
      },
    });
  }

  async listByCandidateId(candidateId: string) {
    return prisma.interviewSession.findMany({
      where: { candidateId },
      include: {
        template: {
          include: {
            job: true,
            questions: true
          }
        },
        resume: true,
        answers: true
      },
      orderBy: { createdAt: "desc" },
    });
  }

  async listByTemplateId(templateId: string) {
    return prisma.interviewSession.findMany({
      where: { templateId },
      include: {
        candidate: true,
        resume: true,
        answers: true
      },
      orderBy: { createdAt: "desc" },
    });
  }
}

export const interviewRepository = new InterviewRepository();
