import { NextRequest } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query } = body;

    if (!query || query.length < 3) {
      return Response.json(
        { success: false, error: "Query must be at least 3 characters" },
        { status: 400 }
      );
    }

    // Call the Python backend research endpoint
    const response = await fetch(`${BACKEND_URL}/research`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Backend error:", errorText);
      return Response.json(
        { success: false, error: "Research service error" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return Response.json(data);
  } catch (error) {
    console.error("Research API error:", error);
    return Response.json(
      { success: false, error: "Failed to connect to research service" },
      { status: 500 }
    );
  }
}
