import { NextRequest, NextResponse } from "next/server";

// Reference to the shared store (in production, this would be a database)
const apiKeysStore = new Map<string, { masked_key: string; label?: string; status: string }>();

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ provider: string }> }
) {
  try {
    const { provider } = await params;

    if (!provider) {
      return NextResponse.json(
        { error: "Provider is required" },
        { status: 400 }
      );
    }

    if (!apiKeysStore.has(provider)) {
      return NextResponse.json(
        { error: "API key not found" },
        { status: 404 }
      );
    }

    apiKeysStore.delete(provider);

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to delete API key" },
      { status: 500 }
    );
  }
}
