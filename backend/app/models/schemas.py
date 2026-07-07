from pydantic import BaseModel, EmailStr


class VideoOut(BaseModel):
    id: str
    title: str
    status: str
    duration_seconds: float
    source_url: str | None = None
    language: str = "en"

    class Config:
        from_attributes = True


class VideoImportRequest(BaseModel):
    url: str


class TranscriptSegmentOut(BaseModel):
    start_seconds: float
    end_seconds: float
    speaker: str | None
    text: str
    ocr_text: str = ""
    chapter_title: str | None = None


class ChatRequest(BaseModel):
    video_id: str | None = None
    course_id: str | None = None
    question: str
    target_language: str | None = None


class Citation(BaseModel):
    start_seconds: float
    end_seconds: float
    snippet: str
    video_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]


class NoteOut(BaseModel):
    chapter_title: str
    start_seconds: float
    content_markdown: str

    class Config:
        from_attributes = True


class FlashcardOut(BaseModel):
    id: str
    question: str
    answer: str
    source_seconds: float | None
    due_at: str

    class Config:
        from_attributes = True


class FlashcardReview(BaseModel):
    flashcard_id: str
    quality: int


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    user: UserOut


class CourseCreate(BaseModel):
    name: str
    description: str = ""


class CourseOut(BaseModel):
    id: str
    name: str
    description: str
    video_count: int = 0

    class Config:
        from_attributes = True


class CourseVideoAdd(BaseModel):
    video_id: str


class TeamCreate(BaseModel):
    name: str


class TeamOut(BaseModel):
    id: str
    name: str
    member_count: int = 0

    class Config:
        from_attributes = True


class TeamMemberAdd(BaseModel):
    user_email: str
    role: str = "member"


class AnnotationCreate(BaseModel):
    video_id: str
    start_seconds: float
    end_seconds: float | None = None
    annotation_type: str = "note"
    text: str


class AnnotationOut(BaseModel):
    id: str
    video_id: str
    user_id: str
    start_seconds: float
    end_seconds: float | None
    annotation_type: str
    text: str

    class Config:
        from_attributes = True


class QuizQuestionOut(BaseModel):
    id: str
    question: str
    options: list[str]
    source_seconds: float | None = None


class QuizOut(BaseModel):
    id: str
    title: str
    questions: list[QuizQuestionOut]


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: list[int]


class QuizSubmitResponse(BaseModel):
    score: int
    total: int
    results: list[dict]


class SlideOut(BaseModel):
    id: str
    start_seconds: float
    title: str
    image_url: str
    ocr_text: str

    class Config:
        from_attributes = True


class ProcessingEventOut(BaseModel):
    step: str
    message: str
    progress: int

    class Config:
        from_attributes = True


class AnalyticsOut(BaseModel):
    total_videos: int
    ready_videos: int
    total_flashcards_reviewed: int
    total_quiz_attempts: int
    average_quiz_score: float
    study_hours: float


class TranslateRequest(BaseModel):
    text: str
    target_language: str


class LmsConnectRequest(BaseModel):
    provider: str
    api_url: str = ""
    api_key: str = ""
