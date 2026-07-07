"use client";

import { useEffect, useState } from "react";
import { createAnnotation, getAnnotations, type Annotation } from "@/lib/api";
import { usePlayerStore } from "@/lib/player-store";
import { Bookmark, Highlighter, StickyNote } from "lucide-react";

export function AnnotationsPanel({ videoId, ready }: { videoId: string; ready: boolean }) {
  const [items, setItems] = useState<Annotation[]>([]);
  const [text, setText] = useState("");
  const [type, setType] = useState("note");
  const currentTime = usePlayerStore((s) => s.currentTime);
  const requestSeek = usePlayerStore((s) => s.requestSeek);

  useEffect(() => {
    if (!ready) return;
    getAnnotations(videoId).then(setItems);
  }, [videoId, ready]);

  async function save() {
    if (!text.trim()) return;
    const annotation = await createAnnotation({
      video_id: videoId,
      start_seconds: currentTime,
      text: text.trim(),
      annotation_type: type,
    });
    setItems((prev) => [...prev, annotation]);
    setText("");
  }

  if (!ready) {
    return <p className="py-8 text-center text-sm text-slate-500">Annotations available after processing.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-surface-border p-4">
        <p className="text-xs text-slate-500">Current timestamp: {currentTime.toFixed(1)}s</p>
        <div className="mt-2 flex gap-2">
          {[
            { id: "note", icon: StickyNote, label: "Note" },
            { id: "bookmark", icon: Bookmark, label: "Bookmark" },
            { id: "highlight", icon: Highlighter, label: "Highlight" },
          ].map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              onClick={() => setType(id)}
              className={`inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs ${
                type === id ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-600"
              }`}
            >
              <Icon className="h-3 w-3" />
              {label}
            </button>
          ))}
        </div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Add a note at the current timestamp…"
          className="mt-3 w-full rounded-lg border border-surface-border px-3 py-2 text-sm"
          rows={3}
        />
        <button
          onClick={save}
          className="mt-2 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700"
        >
          Save annotation
        </button>
      </div>

      {items.map((item) => (
        <div key={item.id} className="rounded-xl bg-surface-muted p-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase text-brand-600">{item.annotation_type}</span>
            <button
              onClick={() => requestSeek(item.start_seconds)}
              className="text-xs text-brand-600 hover:underline"
            >
              ▶ {item.start_seconds.toFixed(0)}s
            </button>
          </div>
          <p className="mt-1 text-sm text-slate-700">{item.text}</p>
        </div>
      ))}
    </div>
  );
}
