"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { getAnalytics, type Analytics } from "@/lib/api";
import { BarChart3, BookOpen, Clock, Trophy } from "lucide-react";

export default function AnalyticsPage() {
  const { ownerId } = useAuth();
  const [data, setData] = useState<Analytics | null>(null);

  useEffect(() => {
    getAnalytics(ownerId).then(setData).catch(() => setData(null));
  }, [ownerId]);

  if (!data) {
    return <p className="py-20 text-center text-sm text-slate-500">Loading analytics…</p>;
  }

  const cards = [
    { label: "Total lectures", value: data.total_videos, icon: BookOpen },
    { label: "Ready to study", value: data.ready_videos, icon: BarChart3 },
    { label: "Quiz attempts", value: data.total_quiz_attempts, icon: Trophy },
    { label: "Study hours", value: data.study_hours, icon: Clock },
  ];

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
      <h1 className="text-2xl font-bold text-slate-900">Learning analytics</h1>
      <p className="mt-2 text-sm text-slate-600">Track your progress across lectures and quizzes.</p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map(({ label, value, icon: Icon }) => (
          <div key={label} className="rounded-2xl bg-white p-5 shadow-card ring-1 ring-surface-border">
            <Icon className="h-5 w-5 text-brand-600" />
            <p className="mt-3 text-2xl font-bold text-slate-900">{value}</p>
            <p className="text-xs text-slate-500">{label}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 rounded-2xl bg-white p-6 shadow-card ring-1 ring-surface-border">
        <h2 className="font-semibold text-slate-900">Quiz performance</h2>
        <p className="mt-2 text-3xl font-bold text-brand-600">
          {data.average_quiz_score.toFixed(0)}%
        </p>
        <p className="text-sm text-slate-500">Average score across all quiz attempts</p>
      </div>
    </div>
  );
}
