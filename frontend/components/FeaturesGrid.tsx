import {
  MessageSquare,
  FileText,
  Layers,
  Clock,
  ScanText,
  Brain,
  BookOpen,
  Users,
  BarChart3,
  Download,
  HelpCircle,
  Globe,
  Bookmark,
  Shield,
} from "lucide-react";

const features = [
  { icon: MessageSquare, title: "Timestamp-cited Q&A", desc: "Hybrid vector + BM25 search with clickable citations." },
  { icon: BookOpen, title: "Course mode", desc: "Group lectures and ask questions across an entire course." },
  { icon: FileText, title: "Auto-generated notes", desc: "LLM-named chapters with structured markdown notes." },
  { icon: Layers, title: "Smart flashcards", desc: "SM-2 spaced repetition with source timestamps." },
  { icon: HelpCircle, title: "Practice quizzes", desc: "Auto-generated MCQs with scoring and explanations." },
  { icon: ScanText, title: "Slide extraction + OCR", desc: "Detects slides, whiteboards, and on-screen text." },
  { icon: Brain, title: "Vision AI summaries", desc: "Claude vision describes frames when API key is set." },
  { icon: Bookmark, title: "Annotations", desc: "Bookmarks, highlights, and personal notes on timestamps." },
  { icon: Download, title: "Export", desc: "Download SRT transcripts, Markdown notes, and Anki decks." },
  { icon: Globe, title: "Multilingual", desc: "Translate Q&A answers to Hindi, Spanish, and more." },
  { icon: Users, title: "Teams & workspaces", desc: "Shared course libraries with role-based access." },
  { icon: BarChart3, title: "Analytics", desc: "Track study hours, quiz scores, and lecture progress." },
  { icon: Shield, title: "Audit & LMS", desc: "Compliance logs plus Canvas, Moodle, Classroom integrations." },
  { icon: Clock, title: "Live SSE progress", desc: "Real-time processing updates with progress bar." },
];

export function FeaturesGrid() {
  return (
    <section id="features" className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
      <div className="mb-12 text-center">
        <h2 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Enterprise-ready feature set
        </h2>
        <p className="mx-auto mt-3 max-w-2xl text-slate-600">
          Auth, courses, teams, hybrid RAG, quizzes, annotations, exports, analytics, LMS hooks, and live processing.
        </p>
      </div>
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {features.map(({ icon: Icon, title, desc }) => (
          <div
            key={title}
            className="rounded-xl bg-white p-6 shadow-card ring-1 ring-surface-border transition hover:shadow-elevated"
          >
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
              <Icon className="h-5 w-5" />
            </div>
            <h3 className="font-semibold text-slate-900">{title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-600">{desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
