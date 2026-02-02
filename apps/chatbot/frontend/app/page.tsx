"use client";

import { FormEvent, useEffect, useState } from "react";
import type { ChatMessage } from "@shared/schemas/chat";
import { branding } from "../lib/branding";
import {
  loadAuthToken,
  loginUser,
  registerUser,
  sendChat,
  sendFeedback,
  setAuthToken
} from "../lib/api";

type FeedbackDraft = {
  tag?: string;
  rewriteText?: string;
  status?: "idle" | "sending" | "sent" | "error";
};

const feedbackTags = [
  "too_shy",
  "too_vague",
  "too_repetitive",
  "not_explicit_enough",
  "perfect"
];

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
  const [feedbackDrafts, setFeedbackDrafts] = useState<Record<number, FeedbackDraft>>({});
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [authStatus, setAuthStatus] = useState<"idle" | "pending" | "error">("idle");
  const [authMessage, setAuthMessage] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const existing = loadAuthToken();
    if (existing) {
      setIsAuthenticated(true);
    }
  }, []);

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
      const responseMessage = response.response;
      if (response.message_id && !responseMessage.id) {
        responseMessage.id = response.message_id;
      }
      setMessages((prev) => [...prev, responseMessage]);
    } finally {
      setPending(false);
    }
  };

  const handleAuth = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!username.trim() || !password) {
      setAuthStatus("error");
      setAuthMessage("Enter a username and password.");
      return;
    }
    setAuthStatus("pending");
    setAuthMessage(null);
    const payload = { username: username.trim(), password };
    const response =
      authMode === "login" ? await loginUser(payload) : await registerUser(payload);
    if (!response) {
      setAuthStatus("error");
      setAuthMessage("Authentication failed. Try again.");
      return;
    }
    setAuthToken(response.access_token);
    setIsAuthenticated(true);
    setAuthStatus("idle");
    setPassword("");
  };

  const handleLogout = () => {
    setAuthToken(null);
    setIsAuthenticated(false);
    setConversationId(undefined);
    setMessages(initialMessages);
  };

  const updateFeedbackDraft = (messageId: number, patch: Partial<FeedbackDraft>) => {
    setFeedbackDrafts((prev) => ({
      ...prev,
      [messageId]: { ...(prev[messageId] || { status: "idle" }), ...patch }
    }));
  };

  const handleFeedback = async (messageId: number, rating: "thumbs_up" | "thumbs_down") => {
    const draft = feedbackDrafts[messageId] || { status: "idle" };
    updateFeedbackDraft(messageId, { status: "sending" });
    const response = await sendFeedback({
      message_id: messageId,
      rating,
      tags: draft.tag ? [draft.tag] : undefined,
      rewrite_text: draft.rewriteText || undefined
    });
    updateFeedbackDraft(messageId, { status: response.status === "ok" ? "sent" : "error" });
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
          {!isAuthenticated ? (
            <div className="grid gap-6 lg:grid-cols-[1.1fr_1fr]">
              <div className="space-y-4">
                <h2 className="text-2xl font-semibold text-neutral-100">
                  Unlock your private session
                </h2>
                <p className="text-sm text-neutral-400">
                  Create a local account to start chatting. Your data stays in your SQLite database.
                </p>
                <div className="rounded-2xl border border-neutral-800 bg-neutral-950/60 p-5">
                  <form onSubmit={handleAuth} className="flex flex-col gap-4">
                    <div className="flex gap-2">
                      <button
                        type="button"
                        className={
                          authMode === "login"
                            ? "flex-1 rounded-xl border border-red-700/60 bg-red-800/30 px-4 py-2 text-sm text-red-100"
                            : "flex-1 rounded-xl border border-neutral-800 bg-neutral-950/60 px-4 py-2 text-sm text-neutral-300"
                        }
                        onClick={() => setAuthMode("login")}
                      >
                        Log in
                      </button>
                      <button
                        type="button"
                        className={
                          authMode === "register"
                            ? "flex-1 rounded-xl border border-red-700/60 bg-red-800/30 px-4 py-2 text-sm text-red-100"
                            : "flex-1 rounded-xl border border-neutral-800 bg-neutral-950/60 px-4 py-2 text-sm text-neutral-300"
                        }
                        onClick={() => setAuthMode("register")}
                      >
                        Register
                      </button>
                    </div>
                    <input
                      className="rounded-xl border border-neutral-800 bg-neutral-950 px-4 py-3 text-sm text-neutral-100 placeholder:text-neutral-600 focus:border-red-700/70 focus:outline-none"
                      placeholder="Username"
                      value={username}
                      onChange={(event) => setUsername(event.target.value)}
                    />
                    <input
                      className="rounded-xl border border-neutral-800 bg-neutral-950 px-4 py-3 text-sm text-neutral-100 placeholder:text-neutral-600 focus:border-red-700/70 focus:outline-none"
                      placeholder="Password"
                      type="password"
                      value={password}
                      onChange={(event) => setPassword(event.target.value)}
                    />
                    {authMessage ? (
                      <p className="text-xs text-red-300">{authMessage}</p>
                    ) : null}
                    <button
                      type="submit"
                      className="rounded-xl bg-red-700/80 px-6 py-3 text-sm font-semibold text-white transition hover:bg-red-600"
                      disabled={authStatus === "pending"}
                    >
                      {authStatus === "pending"
                        ? "Working..."
                        : authMode === "login"
                          ? "Log in"
                          : "Create account"}
                    </button>
                  </form>
                </div>
              </div>
              <div className="rounded-2xl border border-neutral-800 bg-neutral-950/60 p-5 text-sm text-neutral-300">
                <h3 className="text-lg font-semibold text-neutral-100">What you get</h3>
                <ul className="mt-3 space-y-2 text-neutral-400">
                  <li>• Private session tied to your local account</li>
                  <li>• Feedback tools to shape Nyx responses</li>
                  <li>• Conversations stored locally for training review</li>
                </ul>
              </div>
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between">
                <p className="text-xs uppercase tracking-[0.35em] text-neutral-500">
                  Session Active
                </p>
                <button
                  type="button"
                  className="rounded-full border border-neutral-700 px-4 py-2 text-xs text-neutral-300 transition hover:border-neutral-500"
                  onClick={handleLogout}
                >
                  Log out
                </button>
              </div>
              <div className="mt-6 flex min-h-[340px] flex-col gap-4">
                {messages.map((message, index) => (
                  <div
                    key={`${message.role}-${index}`}
                    className="flex w-full flex-col gap-2"
                  >
                    <div
                      className={
                        message.role === "user"
                          ? "self-end max-w-[75%] rounded-2xl border border-red-900/40 bg-red-950/70 px-4 py-3 text-sm text-red-100"
                          : "self-start max-w-[75%] rounded-2xl border border-neutral-700/60 bg-neutral-800/70 px-4 py-3 text-sm text-neutral-100"
                      }
                    >
                      {message.content}
                    </div>
                    {message.role === "assistant" && message.id ? (
                      <div className="self-start flex flex-wrap items-center gap-3 text-xs text-neutral-400">
                        <button
                          type="button"
                          className="rounded-full border border-neutral-700 px-3 py-1 transition hover:border-neutral-500"
                          onClick={() => handleFeedback(message.id!, "thumbs_up")}
                          disabled={feedbackDrafts[message.id]?.status === "sent"}
                        >
                          👍
                        </button>
                        <button
                          type="button"
                          className="rounded-full border border-neutral-700 px-3 py-1 transition hover:border-neutral-500"
                          onClick={() => handleFeedback(message.id!, "thumbs_down")}
                          disabled={feedbackDrafts[message.id]?.status === "sent"}
                        >
                          👎
                        </button>
                        <select
                          className="rounded-full border border-neutral-700 bg-transparent px-3 py-1"
                          value={feedbackDrafts[message.id]?.tag || ""}
                          onChange={(event) =>
                            updateFeedbackDraft(message.id!, { tag: event.target.value || undefined })
                          }
                        >
                          <option value="">Tag (optional)</option>
                          {feedbackTags.map((tag) => (
                            <option key={tag} value={tag}>
                              {tag}
                            </option>
                          ))}
                        </select>
                        <input
                          className="w-full min-w-[200px] flex-1 rounded-full border border-neutral-700 bg-transparent px-3 py-1"
                          placeholder="Rewrite (optional)"
                          value={feedbackDrafts[message.id]?.rewriteText || ""}
                          onChange={(event) =>
                            updateFeedbackDraft(message.id!, { rewriteText: event.target.value })
                          }
                        />
                        <span className="text-neutral-500">
                          {feedbackDrafts[message.id]?.status === "sent" ? "Feedback saved" : ""}
                          {feedbackDrafts[message.id]?.status === "error" ? "Failed to save" : ""}
                        </span>
                      </div>
                    ) : null}
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
            </>
          )}
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
