import { NextRequest, NextResponse } from "next/server";
import { authenticate } from "@/middleware/auth";
import { dataService } from "@/services/data.service";

export async function GET(req: NextRequest) {
  try {
    // Authenticate user
    const payload = authenticate(req);

    // Fetch user details from MongoDB
    const user = await dataService.findUserById(payload.userId);

    if (!user) {
      return NextResponse.json({ success: false, error: "User not found" }, { status: 404 });
    }

    return NextResponse.json({
      success: true,
      data: { user },
    });
  } catch (error) {
    console.error("Get current user error:", error);
    return NextResponse.json({ success: false, error: "Unauthorized" }, { status: 401 });
  }
}
