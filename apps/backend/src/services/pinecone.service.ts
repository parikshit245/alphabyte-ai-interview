import { Pinecone } from "@pinecone-database/pinecone";

export class PineconeService {
  private client: Pinecone | null = null;
  private indexName: string;

  constructor() {
    this.indexName = process.env.PINECONE_INDEX || "ai-interview";
    const apiKey = process.env.PINECONE_API_KEY;

    if (apiKey) {
      try {
        this.client = new Pinecone({ apiKey });
        console.log("Pinecone client initialized");
      } catch (err) {
        console.error("Failed to initialize Pinecone client:", err);
      }
    } else {
      console.warn("PINECONE_API_KEY not found in environment variables.");
    }
  }

  // Stubbed embedding function - in production use OpenAI/Cohere
  private async generateEmbedding(text: string): Promise<number[]> {
    // Generate a random vector of dimension 1024 (matching our Pinecone index)
    console.log("Generating stub embedding for text length:", text.length);
    return Array(1024)
      .fill(0)
      .map(() => Math.random());
  }

  async upsertResumeVector(resumeId: string, text: string) {
    if (!this.client) {
      console.warn("Pinecone client not initialized, skipping vector upsert.");
      return;
    }

    try {
      const index = this.client.index(this.indexName);
      const vector = await this.generateEmbedding(text);

      await index.upsert({
        records: [
          {
            id: resumeId,
            values: vector,
            metadata: {
              type: "resume",
              text: text.substring(0, 1000), // Store chunk of text in metadata if needed
            },
          },
        ],
      });

      console.log(`Successfully upserted vector for resume: ${resumeId}`);
    } catch (error) {
      console.error(`Failed to upsert vector for resume ${resumeId}:`, error);
      // We do NOT throw here to avoid blocking the main flow
    }
  }

  // Upsert resume with metadata (full record storage in Pinecone)
  async upsertResumeRecord(id: string, text: string, metadata: Record<string, any>) {
    if (!this.client) {
      console.warn("Pinecone client not initialized, skipping record upsert.");
      return;
    }

    try {
      const index = this.client.index(this.indexName);
      const vector = await this.generateEmbedding(text);

      await index.upsert({
        records: [
          {
            id,
            values: vector,
            metadata: {
              ...metadata,
              type: "resume",
            },
          },
        ],
      });

      console.log(`Upserted resume record ${id} to Pinecone`);
    } catch (error) {
      console.error(`Failed to upsert resume record ${id}:`, error);
    }
  }

  // Retrieve resumes for a given user by metadata filter
  async getResumesByUser(userId: string) {
    if (!this.client) {
      console.warn("Pinecone client not initialized, cannot query resumes.");
      return [] as any[];
    }

    try {
      const index = this.client.index(this.indexName);
      // Use a zero vector for metadata-only query and filter by userId
      const zeroVector = Array(1024).fill(0);
      const result = await index.query({
        vector: zeroVector,
        topK: 1000,
        includeMetadata: true,
        filter: { userId: userId, type: "resume" },
      });

      const matches = (result.matches || []) as any[];
      return matches.map((m) => ({ id: m.id, score: m.score, metadata: m.metadata }));
    } catch (error) {
      console.error(`Failed to query resumes for user ${userId}:`, error);
      return [] as any[];
    }
  }

  /**
   * General-purpose data record upsert (for users, resumes, etc.)
   */
  async upsertDataRecord(
    namespace: string,
    id: string,
    text: string,
    metadata: Record<string, any>
  ) {
    if (!this.client) {
      console.warn("Pinecone client not initialized, skipping data record upsert.");
      return;
    }

    try {
      const index = this.client.index(this.indexName);
      const vector = await this.generateEmbedding(text);

      // Use namespace for organizing different data types
      await index.upsert({
        records: [
          {
            id: `${namespace}#${id}`, // Composite key: namespace#id
            values: vector,
            metadata: {
              ...metadata,
              namespace,
            },
          },
        ],
        namespace,
      });

      console.log(`✅ Upserted ${namespace} record ${id} to Pinecone`);
    } catch (error) {
      console.error(`Error upserting ${namespace} record ${id}:`, error);
      throw error;
    }
  }

  /**
   * Query data records by metadata filters
   */
  async queryDataByMetadata(
    namespace: string,
    metadataFilter: Record<string, any>,
    topK: number = 100
  ) {
    if (!this.client) {
      console.warn("Pinecone client not initialized, cannot query data records.");
      return [] as any[];
    }

    try {
      const index = this.client.index(this.indexName);
      // Use zero vector for metadata-only filtering
      const zeroVector = Array(1024).fill(0);
      const result = await index.query({
        vector: zeroVector,
        topK,
        includeMetadata: true,
        filter: metadataFilter,
        namespace,
      });

      const matches = (result.matches || []) as any[];
      return matches.map((m) => ({
        id: m.id.split("#")[1] || m.id, // Extract ID from composite key
        metadata: m.metadata,
      }));
    } catch (error) {
      console.error(`Error querying ${namespace} by metadata:`, error);
      return [] as any[];
    }
  }

  /**
   * Delete a data record
   */
  async deleteDataRecord(namespace: string, id: string) {
    if (!this.client) {
      console.warn("Pinecone client not initialized, cannot delete record.");
      return;
    }

    try {
      const index = this.client.index(this.indexName);
      await index.deleteOne({ id: `${namespace}#${id}` });
      console.log(`✅ Deleted ${namespace} record ${id} from Pinecone`);
    } catch (error) {
      console.error(`Error deleting ${namespace} record ${id}:`, error);
      throw error;
    }
  }
}

export const pineconeService = new PineconeService();
