import { NextRequest, NextResponse } from "next/server";

export async function GET(
    _req: NextRequest,
    props: { params: Promise<{ id: string }> }
) {
    try {
        // TODO: Implement with Pinecone
        return NextResponse.json(
            { error: "Interview sessions not yet implemented" },
            { status: 501 }
        );
    } catch (error) {
        console.error("Get session error:", error);
        return NextResponse.json(
            { error: "Failed to fetch session" },
            { status: 500 }
        );
    }
}
