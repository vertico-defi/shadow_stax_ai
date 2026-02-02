export type ChatRole = "user" | "assistant" | "system";

export type ChatMessage = {
  id?: number;
  role: ChatRole;
  content: string;
};

export interface ChatRequest {
  user_id?: string;
  conversation_id?: string;
  messages: ChatMessage[];
  stream?: boolean;
}

export interface ChatResponse {
  conversation_id: string;
  response: ChatMessage;
  status: "ok" | "error";
  message_id?: number;
}
