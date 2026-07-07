"use client";

import Link from "next/link";
import { GraduationCap } from "lucide-react";
import { useAuth } from "@/lib/auth";

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-slate-900/95 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600">
            <GraduationCap className="h-4.5 w-4.5 text-white" />
          </div>
          <span className="text-sm font-semibold tracking-tight text-white">
            Lecture Copilot
          </span>
        </Link>
        <nav className="hidden items-center gap-5 sm:flex">
          <Link href="/courses" className="text-sm text-slate-300 hover:text-white">
            Courses
          </Link>
          <Link href="/teams" className="text-sm text-slate-300 hover:text-white">
            Teams
          </Link>
          <Link href="/analytics" className="text-sm text-slate-300 hover:text-white">
            Analytics
          </Link>
          <a href="#features" className="text-sm text-slate-300 hover:text-white">
            Features
          </a>
        </nav>
        <div className="flex items-center gap-3">
          {user ? (
            <>
              <span className="hidden text-xs text-slate-300 sm:inline">{user.name || user.email}</span>
              <button onClick={logout} className="text-xs text-slate-300 hover:text-white">
                Sign out
              </button>
            </>
          ) : (
            <Link href="/login" className="text-xs font-medium text-brand-200 hover:text-white">
              Sign in
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
