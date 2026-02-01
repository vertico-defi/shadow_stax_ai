import type { ChatRequest, ChatResponse } from "@shared/schemas/chat";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    return {
      status: "error",
      conversation_id: "unknown",
      response: {
        role: "assistant",
        content: "Backend unavailable or returned an error."
      }
    };
  }

  return (await response.json()) as ChatResponse;
}
