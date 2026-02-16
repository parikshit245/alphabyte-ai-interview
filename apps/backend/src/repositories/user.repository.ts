import { PrismaClient } from "@repo/database";
import type { User, Role } from "@prisma/client";

const prisma = new PrismaClient();

export class UserRepository {
  async findById(id: string): Promise<User | null> {
    return prisma.user.findUnique({
      where: { id },
      include: { company: true },
    });
  }

  async findByEmail(email: string): Promise<User | null> {
    return prisma.user.findUnique({
      where: { email },
      include: { company: true },
    });
  }

  async create(data: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
    role: Role;
    companyId?: string;
  }): Promise<User> {
    return prisma.user.create({
      data: {
        email: data.email,
        password: data.password,
        firstName: data.firstName,
        lastName: data.lastName,
        role: data.role,
        ...(data.companyId && { companyId: data.companyId }),
      },
      include: { company: true },
    });
  }

  async update(id: string, data: Partial<User>): Promise<User> {
    return prisma.user.update({
      where: { id },
      data,
      include: { company: true },
    });
  }

  async delete(id: string): Promise<User> {
    return prisma.user.update({
      where: { id },
      data: { isActive: false },
      include: { company: true },
    });
  }

  async list(filters?: { role?: Role; companyId?: string }) {
    return prisma.user.findMany({
      where: {
        isActive: true,
        ...(filters?.role && { role: filters.role }),
        ...(filters?.companyId && { companyId: filters.companyId }),
      },
      include: { company: true },
    });
  }
}

export const userRepository = new UserRepository();
