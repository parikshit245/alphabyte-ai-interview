import { NextRequest, NextResponse } from "next/server";
import { verifyRefreshToken } from "@/lib/jwt";
import { authService } from "@/services/auth.service";

export async function POST(request: NextRequest) {
  try {
    const refreshToken = request.cookies.get("refreshToken")?.value;

    if (!refreshToken) {
      return NextResponse.json(
        {
          success: false,
          error: "No refresh token provided",
        },
        { status: 401 }
      );
    }

    const payload = verifyRefreshToken(refreshToken);
    const tokens = await authService.refreshToken(payload);

    const response = NextResponse.json(
      {
        success: true,
        data: {
          accessToken: tokens.accessToken,
        },
      },
      { status: 200 }
    );

    // Update refresh token cookie
    response.cookies.set("refreshToken", tokens.refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60, // 7 days
      path: "/",
    });

    return response;
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: "Invalid or expired refresh token",
      },
      { status: 401 }
    );
  }
}
