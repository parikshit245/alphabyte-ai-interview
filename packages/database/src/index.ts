import { PrismaClient } from "@prisma/client";

export { PrismaClient } from "@prisma/client";
export * from "@prisma/client";

// Create a singleton instance
const globalForPrisma = global as unknown as { prisma: PrismaClient };

export const db = globalForPrisma.prisma || new PrismaClient();

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = db;
}

