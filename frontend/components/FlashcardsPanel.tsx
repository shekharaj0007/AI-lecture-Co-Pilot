"use client";

import { useEffect, useState } from "react";
import { usePlayerStore } from "@/lib/player-store";
import { Layers, RotateCcw, Check } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8011";

type Flashcard = {
  id: string;
  question: string;
  answer: string;
  source_seconds: number | null;
};

export function FlashcardsPanel({ videoId, ready }: { videoId: string; ready: boolean }) {
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [flipped, setFlipped] = useState<Record<string, boolean>>({});
  const requestSeek = usePlayerStore((s) => s.requestSeek);

  useEffect(() => {
    if (!ready) return;
    fetch(`${API_URL}/flashcards/${videoId}/due`)
      .then((r) => r.json())
      .then(setCards)
      .catch(() => setCards([]));
  }, [videoId, ready]);

  async function review(id: string, quality: number) {
    await fetch(`${API_URL}/flashcards/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ flashcard_id: id, quality }),
    });
    setCards((c) => c.filter((card) => card.id !== id));
    setFlipped((f) => {
      const next = { ...f };
      delete next[id];
      return next;
    });
  }

  if (!ready) {
    return <p className="py-8 text-center text-sm text-slate-500">Flashcards generate after processing.</p>;
  }

  if (cards.length === 0) {
    return (
      <div className="flex flex-col items-center py-12 text-center">
        <Layers className="mb-2 h-8 w-8 text-slate-300" />
        <p className="text-sm text-slate-500">No flashcards due — all caught up!</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {cards.map((card) => (
        <div
          key={card.id}
          className="rounded-xl bg-gradient-to-br from-white to-brand-50/30 p-5 ring-1 ring-surface-border"
        >
          <p className="text-xs font-medium uppercase tracking-wide text-brand-600">Flashcard</p>
          <p className="mt-2 text-sm font-medium text-slate-900">
            {flipped[card.id] ? card.answer : card.question}
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              onClick={() => setFlipped((f) => ({ ...f, [card.id]: !f[card.id] }))}
              className="inline-flex items-center gap-1 rounded-lg border border-surface-border px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-white"
            >
              <RotateCcw className="h-3 w-3" />
              Flip
            </button>
            {card.source_seconds != null && (
              <button
                onClick={() => requestSeek(card.source_seconds!)}
                className="rounded-lg border border-brand-200 px-3 py-1.5 text-xs font-medium text-brand-700 hover:bg-brand-50"
              >
                ▶ Source
              </button>
            )}
            <button
              onClick={() => review(card.id, 2)}
              className="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-200"
            >
              Hard
            </button>
            <button
              onClick={() => review(card.id, 4)}
              className="inline-flex items-center gap-1 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700"
            >
              <Check className="h-3 w-3" />
              Got it
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
