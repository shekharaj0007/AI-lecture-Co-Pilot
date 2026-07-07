"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { Users, Plus } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8010";

type Team = { id: string; name: string; member_count: number };

export default function TeamsPage() {
  const { token, authHeaders } = useAuth();
  const [teams, setTeams] = useState<Team[]>([]);
  const [name, setName] = useState("");

  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/teams`, { headers: authHeaders() })
      .then((r) => (r.ok ? r.json() : []))
      .then(setTeams)
      .catch(() => setTeams([]));
  }, [token]);

  async function createTeam(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    const res = await fetch(`${API_URL}/teams`, {
      method: "POST",
      headers: { ...authHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    if (res.ok) {
      const team = await res.json();
      setTeams((t) => [team, ...t]);
      setName("");
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
      <h1 className="text-2xl font-bold text-slate-900">Teams</h1>
      <p className="mt-2 text-sm text-slate-600">Collaborate on shared course libraries. Sign in required.</p>

      <form onSubmit={createTeam} className="mt-8 flex gap-2">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Team name"
          className="flex-1 rounded-xl border border-surface-border px-4 py-2.5 text-sm"
        />
        <button
          type="submit"
          className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          Create
        </button>
      </form>

      <div className="mt-8 space-y-3">
        {teams.map((team) => (
          <div
            key={team.id}
            className="flex items-center gap-3 rounded-xl bg-white px-5 py-4 shadow-card ring-1 ring-surface-border"
          >
            <Users className="h-5 w-5 text-brand-600" />
            <div>
              <p className="font-medium text-slate-900">{team.name}</p>
              <p className="text-xs text-slate-500">{team.member_count} members</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
