import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    try {
        // TODO: Implement interview session creation with Pinecone
        return NextResponse.json(
            { error: "Interview sessions not yet implemented" },
            { status: 501 }
        );
    } catch (error) {
        console.error("Start session error:", error);
        return NextResponse.json(
            { error: "Failed to start session" },
            { status: 500 }
        );
    }
}
