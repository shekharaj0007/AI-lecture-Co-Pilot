"use client";

import { exportUrl } from "@/lib/api";
import { Download } from "lucide-react";

export function ExportMenu({ videoId, ready }: { videoId: string; ready: boolean }) {
  if (!ready) return null;

  const items = [
    { label: "Transcript (SRT)", format: "srt" as const },
    { label: "Notes (Markdown)", format: "md" as const },
    { label: "Flashcards (Anki CSV)", format: "anki" as const },
  ];

  return (
    <div className="flex flex-wrap gap-2">
      {items.map(({ label, format }) => (
        <a
          key={format}
          href={exportUrl(videoId, format)}
          download
          className="inline-flex items-center gap-1.5 rounded-lg border border-surface-border bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-surface-muted"
        >
          <Download className="h-3.5 w-3.5" />
          {label}
        </a>
      ))}
    </div>
  );
}
