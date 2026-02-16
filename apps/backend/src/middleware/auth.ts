import { NextRequest } from "next/server";
import { verifyAccessToken } from "../lib/jwt";
import { JWTPayload } from "@repo/shared-types";

export interface AuthenticatedRequest extends NextRequest {
  user?: JWTPayload;
}

export function authenticate(request: NextRequest): JWTPayload {
  const authHeader = request.headers.get("authorization");

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    throw new Error("Missing or invalid authorization header");
  }

  const token = authHeader.substring(7);

  try {
    const payload = verifyAccessToken(token);
    return payload;
  } catch (error) {
    throw new Error("Invalid or expired token");
  }
}
