"use client";

import { useEffect, useState } from "react";
import { getTranscript, type TranscriptSegment } from "@/lib/api";
import { usePlayerStore } from "@/lib/player-store";
import { User } from "lucide-react";

function formatTime(seconds: number) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function TranscriptPanel({ videoId, ready }: { videoId: string; ready: boolean }) {
  const [segments, setSegments] = useState<TranscriptSegment[]>([]);
  const requestSeek = usePlayerStore((s) => s.requestSeek);

  useEffect(() => {
    if (!ready) return;
    getTranscript(videoId).then(setSegments);
  }, [videoId, ready]);

  if (!ready) {
    return (
      <p className="py-8 text-center text-sm text-slate-500">
        Transcript will appear after processing completes.
      </p>
    );
  }

  if (segments.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-slate-500">No transcript segments yet.</p>
    );
  }

  return (
    <div className="max-h-[480px] space-y-1 overflow-y-auto pr-1">
      {segments.map((seg, i) => (
        <button
          key={i}
          onClick={() => requestSeek(seg.start_seconds)}
          className="group flex w-full gap-3 rounded-lg px-3 py-2.5 text-left transition hover:bg-brand-50"
        >
          <span className="shrink-0 font-mono text-xs text-brand-600 group-hover:underline">
            {formatTime(seg.start_seconds)}
          </span>
          <div className="min-w-0 flex-1">
            {seg.speaker && (
              <span className="mb-0.5 flex items-center gap-1 text-xs text-slate-400">
                <User className="h-3 w-3" />
                {seg.speaker}
              </span>
            )}
            <p className="text-sm text-slate-700">{seg.text}</p>
            {seg.ocr_text && (
              <p className="mt-1 text-xs text-slate-500 italic">On screen: {seg.ocr_text}</p>
            )}
          </div>
        </button>
      ))}
    </div>
  );
}
