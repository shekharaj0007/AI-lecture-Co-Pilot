"use client";

import { useState } from "react";
import { askQuestion, type Citation } from "@/lib/api";
import { usePlayerStore } from "@/lib/player-store";
import { Send, Sparkles, Loader2 } from "lucide-react";

type Message = {
  role: "user" | "assistant";
  text: string;
  citations?: Citation[];
};

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

const SUGGESTIONS = [
  "Summarize the main topics",
  "What formulas were covered?",
  "Explain the key definitions",
];

export function ChatPanel({ videoId, ready = true }: { videoId: string; ready?: boolean }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("");
  const [error, setError] = useState("");
  const requestSeek = usePlayerStore((s) => s.requestSeek);

  async function handleSend(text?: string) {
    const question = (text ?? input).trim();
    if (!question || loading) return;
    setError("");
    setInput("");
    setMessages((m) => [...m, { role: "user", text: question }]);
    setLoading(true);
    try {
      const res = await askQuestion(question, {
        videoId,
        targetLanguage: language || undefined,
      });
      setMessages((m) => [
        ...m,
        { role: "assistant", text: res.answer, citations: res.citations },
      ]);
    } catch {
      setError("Could not get an answer. Check that the backend is running on port 8011.");
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: "Sorry, I couldn't reach the server. Make sure the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const statusHint = !ready
    ? "Still processing — you can type now; answers improve once ready."
    : null;

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden">
      <div className="mb-3 flex shrink-0 items-center justify-between gap-2 border-b border-surface-border pb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-brand-600" />
          <h2 className="text-sm font-semibold text-slate-900">Ask the lecture</h2>
        </div>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="rounded-lg border border-surface-border bg-white px-2 py-1 text-xs text-slate-900"
        >
          <option value="">English</option>
          <option value="Hindi">Hindi</option>
          <option value="Spanish">Spanish</option>
          <option value="French">French</option>
          <option value="German">German</option>
        </select>
      </div>

      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto pr-1">
        {statusHint && (
          <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800 ring-1 ring-amber-200">
            {statusHint}
          </p>
        )}
        {error && (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700 ring-1 ring-red-200">
            {error}
          </p>
        )}
        {messages.length === 0 && (
          <div className="space-y-2 py-4">
            <p className="text-xs text-slate-500">Try asking:</p>
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => handleSend(s)}
                className="block w-full rounded-lg border border-surface-border px-3 py-2 text-left text-sm text-slate-700 hover:border-brand-300 hover:bg-brand-50"
              >
                {s}
              </button>
            ))}
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[90%] rounded-2xl px-4 py-2.5 text-sm ${
                msg.role === "user"
                  ? "bg-brand-600 text-white"
                  : "bg-surface-muted text-slate-800 ring-1 ring-surface-border"
              }`}
            >
              {msg.text}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {msg.citations.map((c, j) => (
                    <button
                      key={j}
                      onClick={() => requestSeek(c.start_seconds)}
                      className="rounded-md bg-white/90 px-2 py-0.5 text-xs font-medium text-brand-700 ring-1 ring-brand-200 hover:bg-brand-50"
                    >
                      ▶ {formatTime(c.start_seconds)}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            Thinking…
          </div>
        )}
      </div>

      <div className="mt-3 flex shrink-0 gap-2 border-t border-surface-border bg-white pt-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              if (!loading) handleSend();
            }
          }}
          placeholder="Ask about this lecture…"
          autoComplete="off"
          className="min-w-0 flex-1 rounded-xl border border-surface-border bg-white px-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
        />
        <button
          type="button"
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-600 text-white hover:bg-brand-700 disabled:opacity-40"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
