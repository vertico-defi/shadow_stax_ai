import type { ChatRequest, ChatResponse } from "@shared/schemas/chat";
import type { FeedbackRequest, FeedbackResponse } from "@shared/schemas/feedback";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

let authToken: string | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
  if (typeof window !== "undefined") {
    if (token) {
      localStorage.setItem("auth_token", token);
    } else {
      localStorage.removeItem("auth_token");
    }
  }
}

export function loadAuthToken() {
  if (typeof window === "undefined") {
    return null;
  }
  authToken = localStorage.getItem("auth_token");
  return authToken;
}

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {})
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

export async function sendFeedback(request: FeedbackRequest): Promise<FeedbackResponse> {
  const response = await fetch(`${API_BASE_URL}/feedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {})
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    return { status: "error" };
  }

  return (await response.json()) as FeedbackResponse;
}

export type AuthPayload = {
  username: string;
  password: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
};

export async function registerUser(payload: AuthPayload): Promise<AuthResponse | null> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    return null;
  }

  return (await response.json()) as AuthResponse;
}

export async function loginUser(payload: AuthPayload): Promise<AuthResponse | null> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    return null;
  }

  return (await response.json()) as AuthResponse;
}
