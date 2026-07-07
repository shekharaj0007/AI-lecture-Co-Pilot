"use client";

import { useEffect, useState } from "react";
import { getQuiz, submitQuiz, type Quiz } from "@/lib/api";
import { usePlayerStore } from "@/lib/player-store";
import { CheckCircle, XCircle } from "lucide-react";

export function QuizPanel({ videoId, ready }: { videoId: string; ready: boolean }) {
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [results, setResults] = useState<{ score: number; total: number; results: Array<{ correct: boolean; explanation: string }> } | null>(null);
  const requestSeek = usePlayerStore((s) => s.requestSeek);

  useEffect(() => {
    if (!ready) return;
    getQuiz(videoId).then(setQuiz);
  }, [videoId, ready]);

  async function handleSubmit() {
    if (!quiz) return;
    const answerList = quiz.questions.map((q) => answers[q.id] ?? -1);
    const res = await submitQuiz(quiz.id, answerList);
    setResults(res);
  }

  if (!ready) {
    return <p className="py-8 text-center text-sm text-slate-500">Quiz generates after processing.</p>;
  }
  if (!quiz || quiz.questions.length === 0) {
    return <p className="py-8 text-center text-sm text-slate-500">No quiz available yet.</p>;
  }
  if (results) {
    return (
      <div className="space-y-4">
        <p className="text-lg font-semibold text-slate-900">
          Score: {results.score}/{results.total}
        </p>
        {quiz.questions.map((q, i) => (
          <div key={q.id} className="rounded-xl border border-surface-border p-4">
            <div className="flex items-start gap-2">
              {results.results[i]?.correct ? (
                <CheckCircle className="h-4 w-4 shrink-0 text-emerald-600" />
              ) : (
                <XCircle className="h-4 w-4 shrink-0 text-red-500" />
              )}
              <div>
                <p className="text-sm font-medium text-slate-900">{q.question}</p>
                <p className="mt-1 text-xs text-slate-500">{results.results[i]?.explanation}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {quiz.questions.map((q) => (
        <div key={q.id} className="rounded-xl border border-surface-border p-4">
          <p className="text-sm font-medium text-slate-900">{q.question}</p>
          <div className="mt-3 space-y-2">
            {q.options.map((opt, idx) => (
              <label key={idx} className="flex cursor-pointer items-center gap-2 text-sm text-slate-700">
                <input
                  type="radio"
                  name={q.id}
                  checked={answers[q.id] === idx}
                  onChange={() => setAnswers((a) => ({ ...a, [q.id]: idx }))}
                />
                {opt}
              </label>
            ))}
          </div>
          {q.source_seconds != null && (
            <button
              onClick={() => requestSeek(q.source_seconds!)}
              className="mt-2 text-xs text-brand-600 hover:underline"
            >
              ▶ Jump to source
            </button>
          )}
        </div>
      ))}
      <button
        onClick={handleSubmit}
        className="w-full rounded-xl bg-brand-600 py-2.5 text-sm font-medium text-white hover:bg-brand-700"
      >
        Submit quiz
      </button>
    </div>
  );
}
