"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { createCourse, getCourseVideos, listCourses, type Course } from "@/lib/api";
import { BookOpen, ChevronRight, Plus } from "lucide-react";

export default function CoursesPage() {
  const { ownerId } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    listCourses(ownerId).then(setCourses);
  }, [ownerId]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    const course = await createCourse(name, description);
    setCourses((c) => [course, ...c]);
    setName("");
    setDescription("");
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
      <h1 className="text-2xl font-bold text-slate-900">Courses</h1>
      <p className="mt-2 text-sm text-slate-600">
        Group lectures and ask questions across an entire course.
      </p>

      <form onSubmit={handleCreate} className="mt-8 rounded-2xl bg-white p-6 shadow-card ring-1 ring-surface-border">
        <h2 className="font-semibold text-slate-900">Create course</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Course name"
            className="rounded-xl border border-surface-border px-4 py-2.5 text-sm"
          />
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Description (optional)"
            className="rounded-xl border border-surface-border px-4 py-2.5 text-sm"
          />
        </div>
        <button
          type="submit"
          className="mt-4 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          Create course
        </button>
      </form>

      <div className="mt-8 space-y-3">
        {courses.map((course) => (
          <Link
            key={course.id}
            href={`/courses/${course.id}`}
            className="flex items-center justify-between rounded-xl bg-white px-5 py-4 shadow-card ring-1 ring-surface-border hover:ring-brand-300"
          >
            <div className="flex items-center gap-3">
              <BookOpen className="h-5 w-5 text-brand-600" />
              <div>
                <p className="font-medium text-slate-900">{course.name}</p>
                <p className="text-xs text-slate-500">
                  {course.video_count} lecture{course.video_count !== 1 ? "s" : ""}
                </p>
              </div>
            </div>
            <ChevronRight className="h-4 w-4 text-slate-400" />
          </Link>
        ))}
        {courses.length === 0 && (
          <p className="py-8 text-center text-sm text-slate-500">No courses yet. Create one above.</p>
        )}
      </div>
    </div>
  );
}
