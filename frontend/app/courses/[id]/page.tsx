"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { addVideoToCourse, askQuestion, getCourseVideos, listVideos } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { ArrowLeft } from "lucide-react";

export default function CourseDetailPage({ params }: { params: { id: string } }) {
  const { ownerId } = useAuth();
  const [videos, setVideos] = useState<Array<{ id: string; title: string; status: string }>>([]);
  const [allVideos, setAllVideos] = useState<Array<{ id: string; title: string }>>([]);
  const [selectedVideo, setSelectedVideo] = useState("");

  useEffect(() => {
    getCourseVideos(params.id).then(setVideos);
    listVideos(ownerId).then((v) => setAllVideos(v.map(({ id, title }) => ({ id, title }))));
  }, [params.id, ownerId]);

  async function handleAdd() {
    if (!selectedVideo) return;
    await addVideoToCourse(params.id, selectedVideo);
    setVideos(await getCourseVideos(params.id));
    setSelectedVideo("");
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <Link href="/courses" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-brand-600">
        <ArrowLeft className="h-4 w-4" />
        Back to courses
      </Link>

      <h1 className="mt-4 text-2xl font-bold text-slate-900">Course workspace</h1>

      <div className="mt-6 rounded-2xl bg-white p-5 shadow-card ring-1 ring-surface-border">
        <h2 className="font-semibold text-slate-900">Lectures in this course</h2>
        <ul className="mt-3 space-y-2">
          {videos.map((v) => (
            <li key={v.id}>
              <Link href={`/video/${v.id}`} className="text-sm text-brand-600 hover:underline">
                {v.title} ({v.status})
              </Link>
            </li>
          ))}
        </ul>
        <div className="mt-4 flex gap-2">
          <select
            value={selectedVideo}
            onChange={(e) => setSelectedVideo(e.target.value)}
            className="flex-1 rounded-xl border border-surface-border px-3 py-2 text-sm"
          >
            <option value="">Add a lecture…</option>
            {allVideos.map((v) => (
              <option key={v.id} value={v.id}>
                {v.title}
              </option>
            ))}
          </select>
          <button
            onClick={handleAdd}
            className="rounded-xl bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            Add
          </button>
        </div>
      </div>

      <div className="mt-6 rounded-2xl bg-white p-5 shadow-card ring-1 ring-surface-border">
        <h2 className="font-semibold text-slate-900">Cross-lecture Q&A</h2>
        <p className="mt-1 text-sm text-slate-500">Ask across all lectures in this course.</p>
        <CourseChat courseId={params.id} disabled={videos.length === 0} />
      </div>
    </div>
  );
}

function CourseChat({ courseId, disabled }: { courseId: string; disabled: boolean }) {
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; text: string }>>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send() {
    if (!input.trim() || disabled) return;
    const question = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", text: question }]);
    setLoading(true);
    try {
      const res = await askQuestion(question, { courseId });
      setMessages((m) => [...m, { role: "assistant", text: res.answer }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mt-4">
      <div className="max-h-64 space-y-3 overflow-y-auto">
        {messages.map((msg, i) => (
          <div key={i} className={`text-sm ${msg.role === "user" ? "text-right text-brand-700" : "text-slate-700"}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <div className="mt-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={disabled || loading}
          placeholder={disabled ? "Add lectures first…" : "Ask about this course…"}
          className="flex-1 rounded-xl border border-surface-border px-4 py-2.5 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 disabled:bg-slate-50"
          onKeyDown={(e) => e.key === "Enter" && !loading && send()}
        />
        <button
          onClick={send}
          disabled={disabled || loading}
          className="rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          Ask
        </button>
      </div>
    </div>
  );
}
