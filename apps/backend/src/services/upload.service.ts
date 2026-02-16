import { writeFile, mkdir } from "fs/promises";
import { join } from "path";
import { v4 as uuidv4 } from "uuid";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";

type UploadResult = { url: string; fileName: string; path: string };

export class UploadService {
  private uploadDir: string;
  private s3Client: S3Client | null = null;
  private bucket?: string;
  private region?: string;

  constructor() {
    this.uploadDir = join(process.cwd(), "uploads");
    this.ensureUploadDir();
    // Initialize S3 client if AWS env vars are present
    const accessKey = process.env.AWS_ACCESS_KEY_ID;
    const secret = process.env.AWS_SECRET_ACCESS_KEY;
    const bucket = process.env.AWS_BUCKET_NAME || process.env.S3_BUCKET;
    const region = process.env.AWS_REGION || process.env.S3_REGION;

    console.log("🔍 Upload Service Init Debug:", {
      hasAccessKey: !!accessKey,
      hasSecret: !!secret,
      bucket,
      region,
    });

    if (accessKey && secret && bucket) {
      try {
        this.s3Client = new S3Client({ region });
        this.bucket = bucket;
        this.region = region;
        console.log("✅ S3 client initialized for bucket", bucket, "in region", region);
      } catch (err) {
        console.error("❌ Failed to initialize S3 client:", err);
      }
    } else {
      console.log("⚠️  S3 not configured. Missing:", {
        accessKey: !!accessKey,
        secret: !!secret,
        bucket: !!bucket,
      });
    }
  }

  private async ensureUploadDir() {
    try {
      await mkdir(this.uploadDir, { recursive: true });
    } catch (error) {
      console.error("Failed to create upload directory:", error);
    }
  }

  async uploadFile(file: File, subfolder: string = "resumes"): Promise<UploadResult> {
    const buffer = Buffer.from(await file.arrayBuffer());
    const uniqueId = uuidv4();
    const safeName = file.name.replace(/[^a-zA-Z0-9.-]/g, "_");
    const fileName = `${uniqueId}-${safeName}`;

    // If S3 is configured, upload to S3
    if (this.s3Client && this.bucket) {
      const key = `${subfolder}/${fileName}`;
      try {
        const command = new PutObjectCommand({
          Bucket: this.bucket,
          Key: key,
          Body: buffer,
          ContentType: (file as any).type || "application/pdf",
        });
        await this.s3Client.send(command);

        // Construct a public URL (may vary depending on bucket policy)
        const url = `https://${this.bucket}.s3.${this.region || "us-east-1"}.amazonaws.com/${key}`;
        console.log("File uploaded to S3:", key, "URL:", url);
        return { url, fileName: file.name, path: key };
      } catch (err) {
        console.error("S3 upload failed, falling back to local file system:", err);
        // fallthrough to local storage
      }
    }

    // Local fallback
    const targetDir = join(this.uploadDir, subfolder);
    await mkdir(targetDir, { recursive: true });
    const filePath = join(targetDir, fileName);
    await writeFile(filePath, buffer);

    const url = `/uploads/${subfolder}/${fileName}`;
    return { url, fileName: file.name, path: filePath };
  }
}

export const uploadService = new UploadService();
