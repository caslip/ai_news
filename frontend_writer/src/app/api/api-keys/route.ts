import { NextRequest, NextResponse } from "next/server";

// Simulated API keys storage (in production, this would be in a database)
// Using localStorage on client side, this is just for API structure
const apiKeysStore = new Map<string, { masked_key: string; label?: string; status: string }>();

export async function GET() {
  try {
    // In production, fetch from database
    const api_keys = Array.from(apiKeysStore.entries()).map(([provider, data]) => ({
      provider,
      ...data,
    }));

    return NextResponse.json({ api_keys });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to fetch API keys" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { provider, api_key, label } = body;

    if (!provider || !api_key) {
      return NextResponse.json(
        { error: "Provider and API key are required" },
        { status: 400 }
      );
    }

    // Validate API key format (basic validation)
    if (api_key.length < 10) {
      return NextResponse.json(
        { error: "Invalid API key format" },
        { status: 400 }
      );
    }

    // Mask the API key for storage (show first 6 and last 4 characters)
    const maskedKey = maskApiKey(api_key);

    // Store the key (in production, encrypt and store in database)
    apiKeysStore.set(provider, {
      masked_key: maskedKey,
      label,
      status: "configured",
    });

    return NextResponse.json({
      success: true,
      api_key: {
        provider,
        masked_key: maskedKey,
        label,
        status: "configured",
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to save API key" },
      { status: 500 }
    );
  }
}

function maskApiKey(key: string): string {
  if (key.length <= 10) return key.slice(0, 3) + "..." + key.slice(-2);
  return key.slice(0, 6) + "..." + key.slice(-4);
}
