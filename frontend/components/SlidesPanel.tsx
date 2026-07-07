"use client";

import { useEffect, useState } from "react";
import { API_URL, getSlides, type Slide } from "@/lib/api";
import { usePlayerStore } from "@/lib/player-store";
import { ImageIcon } from "lucide-react";

export function SlidesPanel({ videoId, ready }: { videoId: string; ready: boolean }) {
  const [slides, setSlides] = useState<Slide[]>([]);
  const requestSeek = usePlayerStore((s) => s.requestSeek);

  useEffect(() => {
    if (!ready) return;
    getSlides(videoId).then(setSlides);
  }, [videoId, ready]);

  if (!ready) {
    return <p className="py-8 text-center text-sm text-slate-500">Slides extract after processing.</p>;
  }
  if (slides.length === 0) {
    return (
      <div className="flex flex-col items-center py-12 text-center">
        <ImageIcon className="mb-2 h-8 w-8 text-slate-300" />
        <p className="text-sm text-slate-500">No slides detected in this lecture.</p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {slides.map((slide) => (
        <div key={slide.id} className="overflow-hidden rounded-xl ring-1 ring-surface-border">
          <img
            src={`${API_URL}${slide.image_url}`}
            alt={slide.title}
            className="aspect-video w-full bg-slate-100 object-cover"
          />
          <div className="p-3">
            <p className="text-sm font-medium text-slate-900">{slide.title}</p>
            {slide.ocr_text && <p className="mt-1 text-xs text-slate-500 line-clamp-2">{slide.ocr_text}</p>}
            <button
              onClick={() => requestSeek(slide.start_seconds)}
              className="mt-2 text-xs text-brand-600 hover:underline"
            >
              ▶ {slide.start_seconds.toFixed(0)}s
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
