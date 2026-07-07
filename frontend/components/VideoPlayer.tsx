"use client";

import { useEffect, useRef } from "react";
import { usePlayerStore } from "@/lib/player-store";
import { Loader2 } from "lucide-react";

export function VideoPlayer({ src, disabled = false }: { src: string; disabled?: boolean }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const seekTo = usePlayerStore((s) => s.seekTo);
  const clearSeek = usePlayerStore((s) => s.clearSeek);
  const setCurrentTime = usePlayerStore((s) => s.setCurrentTime);

  useEffect(() => {
    if (seekTo == null || !videoRef.current) return;
    videoRef.current.currentTime = seekTo;
    videoRef.current.play();
    clearSeek();
  }, [seekTo, clearSeek]);

  return (
    <div className="relative aspect-video w-full bg-slate-950">
      {disabled && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-2 bg-slate-900/90 text-white">
          <Loader2 className="h-8 w-8 animate-spin text-brand-400" />
          <p className="text-sm font-medium">Downloading video…</p>
        </div>
      )}
      <video
        ref={videoRef}
        src={disabled ? undefined : src}
        controls
        className="h-full w-full"
        playsInline
        onTimeUpdate={() => {
          if (videoRef.current) setCurrentTime(videoRef.current.currentTime);
        }}
      />
    </div>
  );
}
