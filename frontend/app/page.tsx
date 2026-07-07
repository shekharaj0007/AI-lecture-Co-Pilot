"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ImportSection } from "@/components/ImportSection";
import { FeaturesGrid } from "@/components/FeaturesGrid";
import { listVideos, type Video } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { ChevronRight, Video as VideoIcon } from "lucide-react";

export default function HomePage() {
  const { ownerId } = useAuth();
  const [recent, setRecent] = useState<Video[]>([]);

  useEffect(() => {
    listVideos(ownerId).then(setRecent).catch(() => setRecent([]));
  }, [ownerId]);

  return (
    <>
      <section className="gradient-hero px-4 pb-16 pt-12 sm:px-6 sm:pb-20 sm:pt-16">
        <div className="mx-auto max-w-4xl text-center">
          <p className="mb-4 inline-block rounded-full bg-white/10 px-4 py-1.5 text-xs font-medium text-indigo-200 ring-1 ring-white/20">
            AI Video Understanding for Enterprise Learning
          </p>
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-5xl sm:leading-tight">
            Turn any lecture into a{" "}
            <span className="text-gradient">searchable, chatable</span> knowledge base
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-base text-slate-300 sm:text-lg">
            Paste a YouTube link or upload a video. Get timestamp-cited Q&A, auto notes,
            transcripts, and flashcards — powered by Whisper, OCR, and RAG.
          </p>
        </div>
        <div className="mx-auto mt-10 max-w-3xl">
          <ImportSection />
        </div>
      </section>

      {recent.length > 0 && (
        <section className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Recent lectures
          </h2>
          <div className="space-y-2">
            {recent.slice(0, 5).map((v) => (
              <Link
                key={v.id}
                href={`/video/${v.id}`}
                className="flex items-center justify-between rounded-xl bg-white px-4 py-3 shadow-card ring-1 ring-surface-border transition hover:ring-brand-300"
              >
                <div className="flex min-w-0 items-center gap-3">
                  <VideoIcon className="h-4 w-4 shrink-0 text-brand-600" />
                  <span className="truncate text-sm font-medium text-slate-800">{v.title}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs ${
                      v.status === "ready"
                        ? "bg-emerald-50 text-emerald-700"
                        : v.status === "failed"
                          ? "bg-red-50 text-red-700"
                          : "bg-amber-50 text-amber-700"
                    }`}
                  >
                    {v.status === "ready" ? "Ready" : v.status === "failed" ? "Failed" : "Processing"}
                  </span>
                  <ChevronRight className="h-4 w-4 text-slate-400" />
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      <FeaturesGrid />

      <footer className="border-t border-surface-border bg-white py-8 text-center text-xs text-slate-500">
        Lecture Copilot — Enterprise AI video intelligence
      </footer>
    </>
  );
}
