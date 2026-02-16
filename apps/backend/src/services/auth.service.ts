import bcrypt from "bcryptjs";
import { RegisterData, AuthTokens, JWTPayload, Role } from "@repo/shared-types";
import { dataService } from "./data.service";
import { generateTokenPair } from "../lib/jwt";

export class AuthService {
  async register(data: RegisterData): Promise<{ user: any; tokens: AuthTokens }> {
    // Check if user already exists
    const existingUser = await dataService.findUserByEmail(data.email);
    if (existingUser) {
      throw new Error("User with this email already exists");
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(data.password, 10);

    // Create user in MongoDB
    const user = await dataService.createUser(
      data.email,
      hashedPassword,
      data.firstName,
      data.lastName,
      data.role,
      data.companyId
    );

    // Generate tokens
    const tokens = generateTokenPair({
      userId: user.id,
      email: user.email,
      role: user.role as Role,
      companyId: user.companyId,
    });

    return { user, tokens };
  }

  async login(email: string, password: string): Promise<{ user: any; tokens: AuthTokens }> {
    // Find user
    const userData = await dataService.findUserByEmail(email);
    if (!userData || !userData.isActive) {
      throw new Error("Invalid credentials");
    }

    // Verify password
    const isValidPassword = await bcrypt.compare(password, userData.passwordHash);
    if (!isValidPassword) {
      throw new Error("Invalid credentials");
    }

    // Build user object
    const user = {
      id: userData.userId,
      email: userData.email,
      firstName: userData.firstName,
      lastName: userData.lastName,
      role: userData.role,
      companyId: userData.companyId,
    };

    // Generate tokens
    const tokens = generateTokenPair({
      userId: user.id,
      email: user.email,
      role: user.role as Role,
      companyId: user.companyId || null,
    });

    return { user, tokens };
  }

  async refreshToken(payload: JWTPayload): Promise<AuthTokens> {
    // Verify user still exists and is active
    const userData = await dataService.findUserById(payload.userId);
    if (!userData || !userData.isActive) {
      throw new Error("User not found or inactive");
    }

    const user = {
      id: userData.userId,
      email: userData.email,
      firstName: userData.firstName,
      lastName: userData.lastName,
      role: userData.role,
      companyId: userData.companyId,
    };

    // Generate new token pair
    return generateTokenPair({
      userId: user.id,
      email: user.email,
      role: user.role as Role,
      companyId: user.companyId || null,
    });
  }
}

export const authService = new AuthService();
