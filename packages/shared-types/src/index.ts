export enum Role {
  CANDIDATE = "CANDIDATE",
  RECRUITER = "RECRUITER",
  ADMIN = "ADMIN",
  SUPER_ADMIN = "SUPER_ADMIN",
}

export enum InterviewStatus {
  SCHEDULED = "SCHEDULED",
  IN_PROGRESS = "IN_PROGRESS",
  COMPLETED = "COMPLETED",
  CANCELLED = "CANCELLED",
  NO_SHOW = "NO_SHOW",
}

export enum PipelineStage {
  APPLIED = "APPLIED",
  SCREENING = "SCREENING",
  INTERVIEW = "INTERVIEW",
  OFFER = "OFFER",
  HIRED = "HIRED",
  REJECTED = "REJECTED",
}

export interface User {
  id: string;
  email: string;
  role: Role;
  firstName: string;
  lastName: string;
  companyId: string | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface Company {
  id: string;
  name: string;
  domain: string;
  plan: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Resume {
  id: string;
  candidateId: string;
  fileUrl: string;
  parsedData: Record<string, unknown>;
  skills: string[];
  experience: number;
  education: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Job {
  id: string;
  companyId: string;
  title: string;
  description: string;
  requirements: string[];
  skills: string[];
  experience: number;
  location: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface InterviewSession {
  id: string;
  candidateId: string;
  jobId: string;
  recruiterId: string;
  scheduledAt: Date;
  startedAt: Date | null;
  completedAt: Date | null;
  status: InterviewStatus;
  duration: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface InterviewQuestion {
  id: string;
  sessionId: string;
  question: string;
  category: string;
  difficulty: string;
  expectedAnswer: string | null;
  order: number;
  createdAt: Date;
}

export interface InterviewResponse {
  id: string;
  questionId: string;
  sessionId: string;
  answer: string;
  audioUrl: string | null;
  videoUrl: string | null;
  duration: number;
  aiScore: number | null;
  aiAnalysis: Record<string, unknown> | null;
  createdAt: Date;
}

export interface Result {
  id: string;
  sessionId: string;
  candidateId: string;
  jobId: string;
  overallScore: number;
  technicalScore: number;
  behavioralScore: number;
  communicationScore: number;
  integrityScore: number;
  matchScore: number;
  recommendation: string;
  strengths: string[];
  weaknesses: string[];
  summary: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ProctoringLog {
  id: string;
  sessionId: string;
  timestamp: Date;
  eventType: string;
  severity: string;
  details: Record<string, unknown>;
  createdAt: Date;
}

export interface PipelineStatus {
  id: string;
  candidateId: string;
  jobId: string;
  stage: PipelineStage;
  notes: string | null;
  updatedBy: string;
  createdAt: Date;
  updatedAt: Date;
}

// Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: Role;
  companyId?: string;
}

export interface JWTPayload {
  userId: string;
  email: string;
  role: Role;
  companyId: string | null;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

// AI JSON-RPC types
export interface JSONRPCRequest {
  jsonrpc: "2.0";
  method: string;
  params: Record<string, unknown>;
  id: number;
}

export interface JSONRPCResponse {
  jsonrpc: "2.0";
  result?: unknown;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
  id: number;
}

export interface ParseResumeParams {
  resumeUrl: string;
}

export interface GenerateQuestionsParams {
  jobId: string;
  resumeId: string;
  count: number;
}

export interface EvaluateAnswerParams {
  questionId: string;
  answer: string;
}

export interface CalculateMatchScoreParams {
  resumeId: string;
  jobId: string;
}

export interface BehavioralAnalysisParams {
  sessionId: string;
  responses: string[];
}

export interface IntegrityScoringParams {
  sessionId: string;
  proctoringLogs: string[];
}
