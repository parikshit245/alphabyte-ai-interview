import { db, Role } from "@repo/database";

/**
 * Data Service - MongoDB/Prisma Data Layer
 * Handles all structured data storage for users, resumes, etc.
 */
export class DataService {
  /**
   * Create/Store a user
   */
  async createUser(
    email: string,
    passwordHash: string,
    firstName: string,
    lastName: string,
    role: string,
    companyId?: string
  ) {
    const user = await db.user.create({
      data: {
        email,
        password: passwordHash,
        firstName,
        lastName,
        role: role as Role,
        companyId: companyId || null,
        isActive: true,
      },
    });

    return {
      id: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      role: user.role,
      companyId: user.companyId,
      isActive: user.isActive,
    };
  }

  /**
   * Find user by email
   */
  async findUserByEmail(email: string) {
    try {
      const user = await db.user.findUnique({
        where: { email },
      });
      
      if (!user) return null;

      return {
        id: user.id,
        userId: user.id,
        email: user.email,
        passwordHash: user.password,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        companyId: user.companyId,
        isActive: user.isActive,
        createdAt: user.createdAt.toISOString(),
      };
    } catch (error) {
      console.error("Error finding user by email:", error);
      return null;
    }
  }

  /**
   * Find user by ID
   */
  async findUserById(userId: string) {
    try {
      const user = await db.user.findUnique({
        where: { id: userId },
      });

      if (!user) return null;

      return {
        id: user.id,
        userId: user.id,
        email: user.email,
        passwordHash: user.password,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        companyId: user.companyId,
        isActive: user.isActive,
        createdAt: user.createdAt.toISOString(),
      };
    } catch (error) {
      console.error("Error finding user by ID:", error);
      return null;
    }
  }

  /**
   * Store resume metadata
   */
  async createResumeRecord(userData: {
    userId: string;
    fileName: string;
    fileUrl: string;
    rawText: string;
    createdAt: string;
  }) {
    const resume = await db.resume.create({
      data: {
        userId: userData.userId,
        fileName: userData.fileName,
        fileUrl: userData.fileUrl,
        rawText: userData.rawText,
        parsedData: {},
      },
    });

    return {
      id: resume.id,
      userId: resume.userId,
      fileName: resume.fileName,
      fileUrl: resume.fileUrl,
      createdAt: resume.createdAt.toISOString(),
    };
  }

  /**
   * Get all resumes by user ID
   */
  async getResumesByUser(userId: string) {
    try {
      const resumes = await db.resume.findMany({
        where: { userId },
        orderBy: { createdAt: "desc" },
      });

      return resumes.map((r) => ({
        id: r.id,
        fileName: r.fileName,
        fileUrl: r.fileUrl,
        createdAt: r.createdAt.toISOString(),
        rawText: r.rawText || "",
      }));
    } catch (error) {
      console.error("Error fetching resumes for user:", error);
      return [];
    }
  }

  /**
   * Delete a resume record
   */
  async deleteResume(resumeId: string) {
    try {
      await db.resume.delete({
        where: { id: resumeId },
      });
      return true;
    } catch (error) {
      console.error("Error deleting resume:", error);
      return false;
    }
  }

  /**
   * Delete user
   */
  async deleteUser(userId: string) {
    try {
      await db.user.delete({
        where: { id: userId },
      });
      return true;
    } catch (error) {
      console.error("Error deleting user:", error);
      return false;
    }
  }
}

export const dataService = new DataService();
