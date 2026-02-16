import { v4 as uuidv4 } from "uuid";
import { pineconeService } from "@/services/pinecone.service";

/**
 * Pinecone Data Layer Service
 * Handles all structured data storage for users, resumes, etc.
 * Uses Pinecone namespaces to organize different data types.
 */
export class PineconeDataService {
  private usersNamespace = "users";
  private resumesNamespace = "resumes";

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
    const userId = uuidv4();
    const metadata = {
      userId,
      email,
      passwordHash,
      firstName,
      lastName,
      role,
      companyId: companyId || null,
      isActive: true,
      createdAt: new Date().toISOString(),
    };

    await pineconeService.upsertDataRecord(
      this.usersNamespace,
      userId,
      email, // Use email as embedding text for some semantic search capability
      metadata
    );

    return {
      id: userId,
      email,
      firstName,
      lastName,
      role,
      companyId: companyId || null,
      isActive: true,
    };
  }

  /**
   * Find user by email
   */
  async findUserByEmail(email: string) {
    try {
      const results = await pineconeService.queryDataByMetadata(this.usersNamespace, { email });
      return results.length > 0 ? results[0] : null;
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
      const results = await pineconeService.queryDataByMetadata(this.usersNamespace, { userId });
      return results.length > 0 ? results[0] : null;
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
    const resumeId = uuidv4();
    const metadata = {
      resumeId,
      userId: userData.userId,
      fileName: userData.fileName,
      fileUrl: userData.fileUrl,
      rawText: userData.rawText,
      createdAt: userData.createdAt,
    };

    await pineconeService.upsertDataRecord(
      this.resumesNamespace,
      resumeId,
      userData.rawText, // Use rawText for semantic search
      metadata
    );

    return {
      id: resumeId,
      userId: userData.userId,
      fileName: userData.fileName,
      fileUrl: userData.fileUrl,
      createdAt: userData.createdAt,
    };
  }

  /**
   * Get all resumes by user ID
   */
  async getResumesByUser(userId: string) {
    try {
      const results = await pineconeService.queryDataByMetadata(this.resumesNamespace, { userId });
      return results.map((r) => ({
        id: r.id,
        fileName: r.metadata?.fileName || "unknown",
        fileUrl: r.metadata?.fileUrl || "",
        createdAt: r.metadata?.createdAt || null,
        rawText: r.metadata?.rawText || "",
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
      await pineconeService.deleteDataRecord(this.resumesNamespace, resumeId);
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
      await pineconeService.deleteDataRecord(this.usersNamespace, userId);
      return true;
    } catch (error) {
      console.error("Error deleting user:", error);
      return false;
    }
  }
}

export const pineconeDataService = new PineconeDataService();
