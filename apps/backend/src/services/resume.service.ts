import { uploadService } from "@/services/upload.service";
import { dataService } from "@/services/data.service";

// Dynamic import for pdf-parse to handle ESM/CJS compatibility
const parsePdf = async (buffer: Buffer) => {
  const pdfParse = (await import("pdf-parse")) as any;
  return pdfParse(buffer);
};

export class ResumeService {
  async uploadResume(userId: string, file: File) {
    // 1. Extract text from the uploaded file
    let rawText = "";
    try {
      const buffer = Buffer.from(await file.arrayBuffer());
      if (file.name.toLowerCase().endsWith(".pdf")) {
        const data = await parsePdf(buffer);
        rawText = data.text;
      } else {
        console.warn("Text extraction only supported for PDF currently.");
      }
    } catch (e) {
      console.error("Failed to extract text from resume:", e);
      rawText = "Text extraction failed.";
    }

    // 2. Upload file to S3 (or local fallback)
    const { url, fileName } = await uploadService.uploadFile(file, "resumes");

    // 3. Create resume record in MongoDB
    const resume = await dataService.createResumeRecord({
      userId,
      fileName,
      fileUrl: url,
      rawText,
      createdAt: new Date().toISOString(),
    });

    console.log("✅ Resume uploaded and stored in MongoDB:", resume.id);
    return resume;
  }

  async getResumesByUser(userId: string) {
    return dataService.getResumesByUser(userId);
  }
}

export const resumeService = new ResumeService();
