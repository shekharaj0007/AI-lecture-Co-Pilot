const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8011";

function getToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("lc_token");
}

function headers(extra: Record<string, string> = {}) {
  const token = getToken();
  return {
    ...extra,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export type Video = {
  id: string;
  title: string;
  status: string;
  duration_seconds: number;
  source_url?: string | null;
  language?: string;
};

export type Citation = {
  start_seconds: number;
  end_seconds: number;
  snippet: string;
  video_id?: string | null;
};

export type ChatResponse = {
  answer: string;
  citations: Citation[];
};

export type NoteEntry = {
  chapter_title: string;
  start_seconds: number;
  content_markdown: string;
};

export type TranscriptSegment = {
  start_seconds: number;
  end_seconds: number;
  speaker: string | null;
  text: string;
  ocr_text: string;
  chapter_title: string | null;
};

export type Course = {
  id: string;
  name: string;
  description: string;
  video_count: number;
};

export type QuizQuestion = {
  id: string;
  question: string;
  options: string[];
  source_seconds: number | null;
};

export type Quiz = {
  id: string;
  title: string;
  questions: QuizQuestion[];
};

export type Annotation = {
  id: string;
  video_id: string;
  user_id: string;
  start_seconds: number;
  end_seconds: number | null;
  annotation_type: string;
  text: string;
};

export type Slide = {
  id: string;
  start_seconds: number;
  title: string;
  image_url: string;
  ocr_text: string;
};

export type Analytics = {
  total_videos: number;
  ready_videos: number;
  total_flashcards_reviewed: number;
  total_quiz_attempts: number;
  average_quiz_score: number;
  study_hours: number;
};

export async function getVideo(id: string): Promise<Video> {
  const res = await fetch(`${API_URL}/videos/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load video");
  return res.json();
}

export async function listVideos(ownerId: string): Promise<Video[]> {
  const res = await fetch(`${API_URL}/videos?owner_id=${ownerId}`, {
    cache: "no-store",
    headers: headers(),
  });
  if (!res.ok) return [];
  return res.json();
}

export async function getNotes(videoId: string): Promise<NoteEntry[]> {
  const res = await fetch(`${API_URL}/notes/${videoId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load notes");
  return res.json();
}

export async function getTranscript(videoId: string): Promise<TranscriptSegment[]> {
  const res = await fetch(`${API_URL}/transcript/${videoId}`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export async function askQuestion(
  question: string,
  opts: { videoId?: string; courseId?: string; targetLanguage?: string }
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: headers({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      video_id: opts.videoId,
      course_id: opts.courseId,
      question,
      target_language: opts.targetLanguage,
    }),
  });
  if (!res.ok) throw new Error("Failed to get an answer");
  return res.json();
}

export async function uploadVideo(file: File, ownerId: string): Promise<Video> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/videos/upload?owner_id=${ownerId}`, {
    method: "POST",
    headers: headers(),
    body: form,
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function importVideoFromUrl(url: string, ownerId: string): Promise<Video> {
  const res = await fetch(`${API_URL}/videos/import-url?owner_id=${ownerId}`, {
    method: "POST",
    headers: headers({ "Content-Type": "application/json" }),
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || "Import failed");
  }
  return res.json();
}

export async function listCourses(ownerId: string): Promise<Course[]> {
  const res = await fetch(`${API_URL}/courses?owner_id=${ownerId}`, {
    headers: headers(),
  });
  if (!res.ok) return [];
  return res.json();
}

export async function createCourse(name: string, description: string): Promise<Course> {
  const res = await fetch(`${API_URL}/courses`, {
    method: "POST",
    headers: headers({ "Content-Type": "application/json" }),
    body: JSON.stringify({ name, description }),
  });
  if (!res.ok) throw new Error("Failed to create course");
  return res.json();
}

export async function getCourseVideos(courseId: string) {
  const res = await fetch(`${API_URL}/courses/${courseId}/videos`, { headers: headers() });
  if (!res.ok) return [];
  return res.json();
}

export async function addVideoToCourse(courseId: string, videoId: string) {
  await fetch(`${API_URL}/courses/${courseId}/videos`, {
    method: "POST",
    headers: headers({ "Content-Type": "application/json" }),
    body: JSON.stringify({ video_id: videoId }),
  });
}

export async function getQuiz(videoId: string): Promise<Quiz | null> {
  const res = await fetch(`${API_URL}/quizzes/${videoId}`, { headers: headers() });
  if (!res.ok) return null;
  return res.json();
}

export async function submitQuiz(quizId: string, answers: number[]) {
  const res = await fetch(`${API_URL}/quizzes/submit`, {
    method: "POST",
    headers: headers({ "Content-Type": "application/json" }),
    body: JSON.stringify({ quiz_id: quizId, answers }),
  });
  if (!res.ok) throw new Error("Submit failed");
  return res.json();
}

export async function getAnnotations(videoId: string): Promise<Annotation[]> {
  const res = await fetch(`${API_URL}/annotations/${videoId}`, { headers: headers() });
  if (!res.ok) return [];
  return res.json();
}

export async function createAnnotation(body: {
  video_id: string;
  start_seconds: number;
  text: string;
  annotation_type?: string;
}) {
  const res = await fetch(`${API_URL}/annotations`, {
    method: "POST",
    headers: headers({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error("Failed to save annotation");
  return res.json();
}

export async function getSlides(videoId: string): Promise<Slide[]> {
  const res = await fetch(`${API_URL}/slides/${videoId}`, { headers: headers() });
  if (!res.ok) return [];
  return res.json();
}

export async function getAnalytics(ownerId: string): Promise<Analytics> {
  const res = await fetch(`${API_URL}/analytics?owner_id=${ownerId}`, { headers: headers() });
  if (!res.ok) throw new Error("Failed to load analytics");
  return res.json();
}

export function exportUrl(videoId: string, format: "srt" | "md" | "anki") {
  const paths = { srt: "transcript.srt", md: "notes.md", anki: "anki.csv" };
  return `${API_URL}/export/${videoId}/${paths[format]}`;
}

export async function regenerateAiOutputs(videoId: string): Promise<void> {
  const res = await fetch(`${API_URL}/videos/${videoId}/regenerate-ai`, {
    method: "POST",
    headers: headers(),
  });
  if (!res.ok) throw new Error("Regeneration failed");
}

export function processingEventsUrl(videoId: string) {
  return `${API_URL}/events/videos/${videoId}/stream`;
}

export { API_URL };
