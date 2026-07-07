"use client";

import { CheckCircle2, Circle, Loader2, XCircle } from "lucide-react";

const STEPS = [
  { key: "downloading", label: "Download" },
  { key: "uploaded", label: "Queued" },
  { key: "transcribing", label: "Transcribe" },
  { key: "detecting_scenes", label: "Scenes" },
  { key: "extracting_text", label: "OCR" },
  { key: "diarizing", label: "Speakers" },
  { key: "fusing_timeline", label: "Timeline" },
  { key: "indexing", label: "Index" },
  { key: "generating_notes_and_flashcards", label: "Generate" },
  { key: "ready", label: "Ready" },
];

const ORDER = STEPS.map((s) => s.key);

function stepIndex(status: string) {
  const i = ORDER.indexOf(status);
  return i === -1 ? 0 : i;
}

export function ProcessingStatus({
  status,
  progress = 0,
  message = "",
}: {
  status: string;
  progress?: number;
  message?: string;
}) {
  const current = stepIndex(status);
  const failed = status === "failed";
  const done = status === "ready";

  if (done) {
    return (
      <div className="flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700 ring-1 ring-emerald-200">
        <CheckCircle2 className="h-3.5 w-3.5" />
        Ready
      </div>
    );
  }

  if (failed) {
    return (
      <div className="flex items-center gap-2 rounded-full bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 ring-1 ring-red-200">
        <XCircle className="h-3.5 w-3.5" />
        Processing failed
      </div>
    );
  }

  return (
    <div className="rounded-xl bg-white p-4 ring-1 ring-surface-border">
      <div className="mb-3 flex items-center justify-between gap-2 text-sm font-medium text-slate-700">
        <div className="flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin text-brand-600" />
          {message || "Processing lecture…"}
        </div>
        {progress > 0 && <span className="text-xs text-brand-600">{progress}%</span>}
      </div>
      {progress > 0 && (
        <div className="mb-3 h-1.5 overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-brand-600 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        {STEPS.slice(0, -1).map((step, i) => {
          const complete = i < current;
          const active = i === current;
          return (
            <span
              key={step.key}
              className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs ${
                complete
                  ? "bg-emerald-50 text-emerald-700"
                  : active
                    ? "bg-brand-50 text-brand-700 ring-1 ring-brand-200"
                    : "bg-slate-100 text-slate-400"
              }`}
            >
              {complete ? (
                <CheckCircle2 className="h-3 w-3" />
              ) : active ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : (
                <Circle className="h-3 w-3" />
              )}
              {step.label}
            </span>
          );
        })}
      </div>
    </div>
  );
}
