import { NextRequest } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Forward to AG-UI backend
    const response = await fetch(`${BACKEND_URL}/copilotkit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    // Check if streaming response
    const contentType = response.headers.get("content-type");
    
    if (contentType?.includes("text/event-stream")) {
      // Return streaming response
      return new Response(response.body, {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
        },
      });
    }

    // Return JSON response
    const data = await response.json();
    return Response.json(data);
    
  } catch (error) {
    console.error("CopilotKit API error:", error);
    return Response.json(
      { error: "Failed to process request" },
      { status: 500 }
    );
  }
}
