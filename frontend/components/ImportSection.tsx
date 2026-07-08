"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Upload,
  Link2,
  Youtube,
  Loader2,
  FileVideo,
  ClipboardPaste,
} from "lucide-react";
import { importVideoFromUrl, uploadVideo } from "@/lib/api";
import { useAuth } from "@/lib/auth";

type Tab = "youtube" | "upload";

export function ImportSection() {
  const [tab, setTab] = useState<Tab>("youtube");
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();
  const { ownerId } = useAuth();

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text.includes("youtube.com") || text.includes("youtu.be") || text.startsWith("http")) {
        setUrl(text.trim());
        setTab("youtube");
      }
    } catch {
      /* clipboard denied */
    }
  };

  const handleYoutubeImport = async () => {
    const trimmed = url.trim();
    if (!trimmed) return;
    setLoading(true);
    setError("");
    try {
      const video = await importVideoFromUrl(trimmed, ownerId);
      router.push(`/video/${video.id}`);
    } catch {
      setError("Could not import video. Make sure the backend is running and the URL is valid.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const video = await uploadVideo(file, ownerId);
      router.push(`/video/${video.id}`);
    } catch {
      setError("Upload failed. Check that the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped?.type.startsWith("video/")) {
      setFile(dropped);
      setTab("upload");
    }
  }, []);

  return (
    <section id="import" className="mx-auto max-w-3xl">
      <div className="overflow-hidden rounded-2xl bg-white shadow-elevated ring-1 ring-surface-border">
        <div className="flex border-b border-surface-border">
          <button
            onClick={() => setTab("youtube")}
            className={`flex flex-1 items-center justify-center gap-2 px-4 py-3.5 text-sm font-medium transition ${
              tab === "youtube"
                ? "border-b-2 border-brand-600 text-brand-600 bg-brand-50/50"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            <Youtube className="h-4 w-4" />
            YouTube / Link
          </button>
          <button
            onClick={() => setTab("upload")}
            className={`flex flex-1 items-center justify-center gap-2 px-4 py-3.5 text-sm font-medium transition ${
              tab === "upload"
                ? "border-b-2 border-brand-600 text-brand-600 bg-brand-50/50"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            <Upload className="h-4 w-4" />
            Upload file
          </button>
        </div>

        <div className="p-6 sm:p-8">
          {tab === "youtube" ? (
            <div className="space-y-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Paste YouTube or video URL
                </label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Link2 className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                    <input
                      type="url"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleYoutubeImport()}
                      placeholder="https://www.youtube.com/watch?v=..."
                      className="w-full rounded-xl border border-surface-border bg-white py-3 pl-10 pr-4 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handlePaste}
                    className="flex items-center gap-1.5 rounded-xl border border-surface-border px-3 py-2 text-sm text-slate-600 hover:bg-surface-muted"
                    title="Paste from clipboard"
                  >
                    <ClipboardPaste className="h-4 w-4" />
                    <span className="hidden sm:inline">Paste</span>
                  </button>
                </div>
              </div>
              <p className="text-xs text-slate-500">
                Supports YouTube, Vimeo, and direct .mp4 links. Playlist URLs import the single video only.
              </p>
              <button
                onClick={handleYoutubeImport}
                disabled={!url.trim() || loading}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-brand-600 py-3.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Starting import…
                  </>
                ) : (
                  <>
                    <Youtube className="h-4 w-4" />
                    Import lecture
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={onDrop}
                className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-12 transition ${
                  dragOver
                    ? "border-brand-500 bg-brand-50"
                    : "border-surface-border bg-surface-muted hover:border-slate-300"
                }`}
              >
                <FileVideo className="mb-3 h-10 w-10 text-slate-400" />
                <p className="mb-1 text-sm font-medium text-slate-700">
                  Drag & drop your lecture video
                </p>
                <p className="mb-4 text-xs text-slate-500">MP4, WebM, MOV — up to 3+ hours</p>
                <label className="cursor-pointer rounded-lg bg-white px-4 py-2 text-sm font-medium text-brand-600 ring-1 ring-surface-border hover:bg-slate-50">
                  Browse files
                  <input
                    type="file"
                    accept="video/*"
                    className="hidden"
                    onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  />
                </label>
                {file && (
                  <p className="mt-3 text-xs text-brand-600">{file.name}</p>
                )}
              </div>
              <button
                onClick={handleUpload}
                disabled={!file || loading}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-brand-600 py-3.5 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Uploading…
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4" />
                    Upload & analyze
                  </>
                )}
              </button>
            </div>
          )}

          {error && (
            <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-100">
              {error}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
