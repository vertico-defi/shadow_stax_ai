"use client";

import { FormEvent, useState } from "react";
import type { ChatMessage } from "@shared/schemas/chat";
import { branding } from "../lib/branding";
import { sendChat } from "../lib/api";

const initialMessages: ChatMessage[] = [
  {
    role: "assistant",
    content:
      "Welcome to your private session. Your conversation stays between you and the system."
  }
];

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!input.trim() || pending) {
      return;
    }

    const userMessage: ChatMessage = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setPending(true);

    try {
      const response = await sendChat({
        conversation_id: conversationId,
        messages: [userMessage],
        stream: false
      });
      setConversationId(response.conversation_id);
      setMessages((prev) => [...prev, response.response]);
    } finally {
      setPending(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-neutral-950 via-neutral-950 to-neutral-900 px-6 py-12">
      <div className="mx-auto flex max-w-4xl flex-col gap-10">
        <header className="space-y-4">
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-neutral-500">
            Private Access
          </p>
          <div className="space-y-2">
            <h1 className="text-4xl font-semibold tracking-tight text-neutral-100 sm:text-5xl">
              {branding.productName}
            </h1>
            <p className="text-lg text-neutral-300">{branding.tagline}</p>
          </div>
          <p className="max-w-2xl text-sm text-neutral-400">
            This is an adult-only, unfiltered conversation space designed for discreet, intimate
            exchanges. Stay in control of the session and set the pace.
          </p>
        </header>

        <section className="rounded-3xl border border-neutral-800 bg-neutral-900/70 p-6 shadow-[0_20px_60px_-40px_rgba(0,0,0,0.8)] backdrop-blur">
          <div className="flex min-h-[340px] flex-col gap-4">
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={
                  message.role === "user"
                    ? "self-end max-w-[75%] rounded-2xl border border-red-900/40 bg-red-950/70 px-4 py-3 text-sm text-red-100"
                    : "self-start max-w-[75%] rounded-2xl border border-neutral-700/60 bg-neutral-800/70 px-4 py-3 text-sm text-neutral-100"
                }
              >
                {message.content}
              </div>
            ))}
          </div>

          <form
            onSubmit={handleSubmit}
            className="mt-6 flex flex-col gap-3 rounded-2xl border border-neutral-800 bg-neutral-950/60 p-4 sm:flex-row"
          >
            <input
              className="flex-1 rounded-xl border border-neutral-800 bg-neutral-950 px-4 py-3 text-sm text-neutral-100 placeholder:text-neutral-600 focus:border-red-700/70 focus:outline-none"
              placeholder="Begin your explicit conversation..."
              value={input}
              onChange={(event) => setInput(event.target.value)}
            />
            <button
              type="submit"
              className="rounded-xl bg-red-700/80 px-6 py-3 text-sm font-semibold text-white transition hover:bg-red-600"
            >
              {pending ? "Connecting..." : "Send"}
            </button>
          </form>
        </section>

        <footer className="flex flex-col items-start gap-2 text-xs text-neutral-500 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-col gap-1 sm:flex-row sm:gap-3">
            <span>{branding.attribution}</span>
            <span>{branding.copyright}</span>
          </div>
          <span>{branding.ageNotice}</span>
        </footer>
      </div>
    </main>
  );
}
