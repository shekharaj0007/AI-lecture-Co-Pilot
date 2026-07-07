"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getNotes, getVideo, processingEventsUrl, type NoteEntry, type Video } from "@/lib/api";
import { ChatPanel } from "@/components/ChatPanel";
import { FlashcardsPanel } from "@/components/FlashcardsPanel";
import { TranscriptPanel } from "@/components/TranscriptPanel";
import { ProcessingStatus } from "@/components/ProcessingStatus";
import { VideoPlayer } from "@/components/VideoPlayer";
import { QuizPanel } from "@/components/QuizPanel";
import { AnnotationsPanel } from "@/components/AnnotationsPanel";
import { SlidesPanel } from "@/components/SlidesPanel";
import { ExportMenu } from "@/components/ExportMenu";
import {
  ArrowLeft,
  ExternalLink,
  MessageSquare,
  FileText,
  Layers,
  List,
  HelpCircle,
  Bookmark,
  ImageIcon,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8010";

type Tab = "chat" | "transcript" | "notes" | "flashcards" | "quiz" | "annotations" | "slides";

export function VideoWorkspace({ video: initialVideo }: { video: Video }) {
  const [video, setVideo] = useState(initialVideo);
  const [notes, setNotes] = useState<NoteEntry[]>([]);
  const [tab, setTab] = useState<Tab>("chat");
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState("");

  const processing = video.status !== "ready" && video.status !== "failed";

  useEffect(() => {
    if (video.status === "ready" || video.status === "failed") return;

    const es = new EventSource(processingEventsUrl(video.id));
    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setProgress(data.progress ?? 0);
        setProgressMessage(data.message ?? "");
        if (data.step === "ready" || data.step === "failed") {
          getVideo(video.id).then(setVideo);
          es.close();
        }
      } catch {
        /* ignore */
      }
    };

    const timer = setInterval(async () => {
      const next = await getVideo(video.id);
      setVideo(next);
    }, 5000);

    return () => {
      es.close();
      clearInterval(timer);
    };
  }, [video.id, video.status]);

  useEffect(() => {
    if (video.status !== "ready") return;
    getNotes(video.id).then(setNotes).catch(() => setNotes([]));
  }, [video.id, video.status]);

  const streamUrl = `${API_URL}/videos/${video.id}/stream`;
  const tabs: { id: Tab; label: string; icon: typeof MessageSquare }[] = [
    { id: "chat", label: "Q&A", icon: MessageSquare },
    { id: "transcript", label: "Transcript", icon: List },
    { id: "notes", label: "Notes", icon: FileText },
    { id: "flashcards", label: "Cards", icon: Layers },
    { id: "quiz", label: "Quiz", icon: HelpCircle },
    { id: "annotations", label: "Notes+", icon: Bookmark },
    { id: "slides", label: "Slides", icon: ImageIcon },
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
      <Link
        href="/"
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-brand-600"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to home
      </Link>

      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="truncate text-xl font-bold text-slate-900 sm:text-2xl">{video.title}</h1>
          {video.source_url && (
            <a
              href={video.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 inline-flex items-center gap-1 text-sm text-brand-600 hover:underline"
            >
              <ExternalLink className="h-3.5 w-3.5" />
              Source link
            </a>
          )}
        </div>
        <div className="flex flex-col items-end gap-2">
          {!processing && video.status === "ready" && (
            <span className="shrink-0 rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 ring-1 ring-emerald-200">
              Ready
            </span>
          )}
          <ExportMenu videoId={video.id} ready={video.status === "ready"} />
        </div>
      </div>

      {processing && (
        <div className="mb-6">
          <ProcessingStatus status={video.status} progress={progress} message={progressMessage} />
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="space-y-4 lg:col-span-3">
          <div className="overflow-hidden rounded-2xl bg-black shadow-elevated ring-1 ring-slate-800">
            <VideoPlayer src={streamUrl} disabled={video.status === "downloading"} />
          </div>
        </div>

        <div className="flex h-[520px] flex-col lg:col-span-2">
          <div className="flex shrink-0 overflow-x-auto rounded-t-2xl border border-b-0 border-surface-border bg-white p-1">
            {tabs.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setTab(id)}
                className={`flex shrink-0 items-center justify-center gap-1 rounded-xl px-2 py-2.5 text-xs font-medium transition sm:px-3 ${
                  tab === id
                    ? "bg-brand-600 text-white shadow-sm"
                    : "text-slate-500 hover:bg-surface-muted hover:text-slate-700"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{label}</span>
              </button>
            ))}
          </div>
          <div className="flex min-h-0 flex-1 flex-col rounded-b-2xl rounded-tr-2xl bg-white p-4 shadow-card ring-1 ring-surface-border sm:p-5">
            {tab === "chat" && (
              <ChatPanel videoId={video.id} ready={video.status === "ready"} />
            )}
            {tab === "transcript" && (
              <TranscriptPanel videoId={video.id} ready={video.status === "ready"} />
            )}
            {tab === "notes" && (
              <NotesContent notes={notes} ready={video.status === "ready"} />
            )}
            {tab === "flashcards" && (
              <FlashcardsPanel videoId={video.id} ready={video.status === "ready"} />
            )}
            {tab === "quiz" && (
              <QuizPanel videoId={video.id} ready={video.status === "ready"} />
            )}
            {tab === "annotations" && (
              <AnnotationsPanel videoId={video.id} ready={video.status === "ready"} />
            )}
            {tab === "slides" && (
              <SlidesPanel videoId={video.id} ready={video.status === "ready"} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function NotesContent({ notes, ready }: { notes: NoteEntry[]; ready: boolean }) {
  if (!ready) {
    return <p className="py-8 text-center text-sm text-slate-500">Notes generate after processing.</p>;
  }
  if (notes.length === 0) {
    return <p className="py-8 text-center text-sm text-slate-500">No notes generated yet.</p>;
  }
  return (
    <div className="max-h-[480px] space-y-6 overflow-y-auto">
      {notes.map((note) => (
        <article key={`${note.chapter_title}-${note.start_seconds}`}>
          <h3 className="font-semibold text-brand-700">{note.chapter_title}</h3>
          <div className="prose prose-sm mt-2 max-w-none text-slate-700">
            <pre className="whitespace-pre-wrap font-sans text-sm">{note.content_markdown}</pre>
          </div>
        </article>
      ))}
    </div>
  );
}
