# CLAUDE.md — Golf Academy Differentiated Learning App

## Project Name: SwingLens

## What This Project Is

An AI-powered video coaching platform for golf academies. Players upload swing videos from their phone. The system extracts key frames, runs pose estimation, compares against the player's personal baseline, and delivers near-instant feedback. Coaches review curated frames (not full videos) and can respond asynchronously. The academy scales coaching capacity 5-10x without adding headcount.

**First customer:** TSG (The School of Golf), Bangalore.

---

## Development Environment Setup

### Prerequisites

- **Python**: 3.11+ managed via `pyenv`. The project uses `pyenv local` to pin the version.
- **Node.js**: 18+ (use `nvm` or system install)
- **Docker & Docker Compose**: For PostgreSQL and Redis in development
- **OS**: macOS (primary dev machine)

### First-Time Setup

```bash
# 1. Clone and enter repo
git clone <repo-url> && cd swinglens

# 2. Python setup (pyenv)
pyenv install 3.11.9      # or latest 3.11.x
pyenv local 3.11.9         # creates .python-version file in repo root
python -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt

# 3. Start infrastructure
docker-compose up -d       # PostgreSQL + Redis

# 4. Run migrations
cd backend && alembic upgrade head && cd ..

# 5. Start backend
cd backend && uvicorn app.main:app --reload --port 8000

# 6. Coach dashboard (separate terminal)
cd coach-dashboard && npm install && npm run dev

# 7. Player app (separate terminal)
cd player-app && npm install && npx expo start
```

### Environment Rules

- Always use the `pyenv` managed Python — never system Python
- Backend virtual environment lives at `backend/.venv/` — activate it before running any Python commands
- Add `.python-version` to the repo (not in `.gitignore`)
- Add `backend/.venv/` to `.gitignore`
- Docker Compose handles PostgreSQL and Redis — never install these locally
- `.env` file lives in repo root, loaded by backend's `config.py` — never commit it, commit `.env.example` instead

---

## Tech Stack

| Layer              | Technology                                                       | Why                                                    |
| ------------------ | ---------------------------------------------------------------- | ------------------------------------------------------ |
| Backend API        | FastAPI (Python 3.11+)                                           | Clean typed APIs, async support, auto Swagger docs     |
| Database           | PostgreSQL 16                                                    | Reliable, great JSON support for keypoints data        |
| Async Jobs         | Celery + Redis                                                   | Video processing pipeline runs async                   |
| Object Storage     | AWS S3                                                           | Videos, extracted frames, annotated images             |
| Pose Estimation    | MediaPipe Pose (Python)                                          | 33 body landmarks, runs on CPU, well-documented        |
| Video Processing   | OpenCV + ffmpeg                                                  | Frame extraction, annotation overlays                  |
| AI Feedback        | Claude API (Sonnet) with Vision                                  | Natural language coaching feedback from frames         |
| Player App         | React Native (Expo) + TypeScript                                 | Cross-platform mobile, shared types with web           |
| Coach Dashboard    | React (Vite) + TypeScript                                        | Web-based, same API as mobile app                      |
| UI Components      | shadcn/ui + Tailwind CSS + Radix UI                              | Accessible, composable, customizable component library |
| Forms              | React Hook Form + Zod                                            | Type-safe form handling with schema validation         |
| Server State       | TanStack Query (React Query) v5                                  | Caching, background refetch, optimistic updates        |
| Client State       | Zustand                                                          | Lightweight, TypeScript-first global state             |
| Routing (Web)      | React Router v6                                                  | Standard, well-supported                               |
| Routing (Mobile)   | Expo Router                                                      | File-based routing for React Native                    |
| HTTP Client        | Axios                                                            | Request/response interceptors for auth                 |
| Auth               | JWT tokens + OTP (phone) for players, email/password for coaches |
| Push Notifications | Firebase Cloud Messaging                                         |
| Deployment         | Docker Compose on a VPS (start simple)                           |

---

## Folder Structure

```
swinglens/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── config.py                # Settings, env vars
│   │   ├── models/                  # SQLAlchemy models
│   │   │   ├── player.py
│   │   │   ├── coach.py
│   │   │   ├── academy.py
│   │   │   ├── video.py
│   │   │   ├── frame.py
│   │   │   ├── comparison.py
│   │   │   └── feedback.py
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── api/                     # Route handlers
│   │   │   ├── auth.py
│   │   │   ├── players.py
│   │   │   ├── coaches.py
│   │   │   ├── videos.py
│   │   │   ├── frames.py
│   │   │   ├── feedback.py
│   │   │   └── admin.py
│   │   ├── services/                # Business logic
│   │   │   ├── video_processor.py   # Orchestrates the pipeline
│   │   │   ├── pose_estimator.py    # MediaPipe wrapper
│   │   │   ├── swing_detector.py    # Detects swing phases from keypoints
│   │   │   ├── angle_calculator.py  # Computes joint angles
│   │   │   ├── comparator.py        # Compares against player baseline
│   │   │   ├── annotator.py         # Generates all 3 frame view modes (raw, overlay, skeleton)
│   │   │   ├── ai_feedback.py       # Claude API integration
│   │   │   └── storage.py           # S3 upload/download
│   │   ├── tasks/                   # Celery async tasks
│   │   │   └── process_video.py
│   │   └── utils/
│   ├── migrations/                  # Alembic migrations
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── coach-dashboard/                 # React web app (Vite + TypeScript)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                  # shadcn/ui components (Button, Dialog, Card, etc.)
│   │   │   ├── frames/             # FrameViewer, FrameComparison, ViewModeToggle
│   │   │   ├── feedback/           # FeedbackCard, AIFeedback, CoachNoteForm
│   │   │   └── layout/             # Sidebar, Header, PageWrapper
│   │   ├── pages/                   # Route-level page components
│   │   ├── hooks/                   # Custom hooks (usePlayer, useVideoUpload, useFrames)
│   │   ├── api/
│   │   │   ├── client.ts           # Axios instance with auth interceptors
│   │   │   └── types.ts            # Shared API request/response types
│   │   ├── schemas/                 # Zod validation schemas (feedback-schema.ts, player-schema.ts)
│   │   ├── stores/                  # Zustand stores (auth-store.ts, ui-store.ts)
│   │   ├── lib/
│   │   │   └── utils.ts            # cn() helper, formatting functions
│   │   └── utils/
│   ├── components.json              # shadcn/ui config
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
├── player-app/                      # React Native (Expo + TypeScript)
│   ├── src/
│   │   ├── screens/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   │   ├── client.ts           # Shared Axios instance
│   │   │   └── types.ts            # Reuse same types as coach-dashboard where possible
│   │   ├── schemas/                 # Zod schemas for forms
│   │   ├── stores/                  # Zustand stores
│   │   └── utils/
│   ├── app/                         # Expo Router file-based routes
│   ├── tsconfig.json
│   └── package.json
├── prompts/                         # Claude API prompt templates
│   ├── swing_analysis.txt
│   ├── baseline_comparison.txt
│   ├── progress_summary.txt
│   └── camera_validation.txt
├── docker-compose.yml
└── CLAUDE.md                        # This file
```

---

## Database Schema

```sql
-- Academies
CREATE TABLE academies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Coaches
CREATE TABLE coaches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID REFERENCES academies(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Players
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    academy_id UUID REFERENCES academies(id),
    coach_id UUID REFERENCES coaches(id),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    handicap DECIMAL(4,1),
    skill_level VARCHAR(20) DEFAULT 'beginner',  -- beginner, intermediate, advanced, pro
    dominant_hand VARCHAR(10) DEFAULT 'right',     -- right, left
    created_at TIMESTAMP DEFAULT NOW()
);

-- Videos
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id),
    s3_key VARCHAR(500) NOT NULL,
    camera_angle VARCHAR(20),           -- dtl (down-the-line), face_on
    club_type VARCHAR(30),              -- driver, iron_3..iron_9, wedge_pw..wedge_lw, putter
    status VARCHAR(20) DEFAULT 'uploading',  -- uploading, processing, analyzed, reviewed, error
    duration_ms INTEGER,
    fps INTEGER,
    error_message TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

-- Frames (extracted key frames from each swing phase)
-- Each frame is stored in 3 versions for the togglable view modes (see "Frame View Modes" section)
CREATE TABLE frames (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id),
    swing_phase VARCHAR(30) NOT NULL,   -- address, takeaway, mid_backswing, top, mid_downswing, impact, mid_follow_through, finish
    frame_number INTEGER NOT NULL,
    s3_key_raw VARCHAR(500),            -- raw photo frame extracted from video (no overlays)
    s3_key_overlay VARCHAR(500),        -- raw photo + pose skeleton + angle annotations drawn on top
    s3_key_skeleton VARCHAR(500),       -- skeleton only on black/dark background (no photo)
    keypoints_json JSONB,               -- MediaPipe 33 landmarks {landmark_id: {x, y, z, visibility}}
    joint_angles_json JSONB,            -- computed angles {angle_name: value_degrees}
    is_reference BOOLEAN DEFAULT FALSE, -- coach-validated "good" frame for this player+phase
    created_at TIMESTAMP DEFAULT NOW()
);

-- Comparisons (current frame vs reference frame)
CREATE TABLE comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    frame_id UUID REFERENCES frames(id),            -- current frame
    reference_frame_id UUID REFERENCES frames(id),  -- player's baseline frame for same phase
    deviation_scores_json JSONB,        -- {angle_name: {current: X, reference: Y, delta: Z, severity: "ok|minor|major"}}
    overall_score DECIMAL(5,2),         -- 0-100 similarity score
    ai_feedback_text TEXT,              -- Claude-generated coaching feedback
    coach_feedback_text TEXT,           -- Coach's manual notes
    coach_approved BOOLEAN,             -- Coach approved/overrode AI feedback
    created_at TIMESTAMP DEFAULT NOW()
);

-- Feedback (aggregated feedback per video)
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id),
    player_id UUID REFERENCES players(id),
    coach_id UUID REFERENCES coaches(id),
    feedback_type VARCHAR(20) NOT NULL,  -- ai_instant, coach_review
    summary TEXT,                         -- overall feedback summary
    drill_recommendations JSONB,         -- [{name, description, video_url}]
    priority_fixes JSONB,                -- [{issue, phase, severity, description}]
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Player progress tracking
CREATE TABLE progress_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id),
    snapshot_date DATE NOT NULL,
    angles_avg_json JSONB,              -- rolling average of key angles
    consistency_score DECIMAL(5,2),
    total_swings INTEGER,
    coach_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Design Conventions

### General Rules

- All endpoints prefixed with `/api/v1/`
- Use UUID for all IDs
- Snake_case for JSON field names
- Always return `{ "data": ... }` for success, `{ "error": { "message": "...", "code": "..." } }` for errors
- Pagination: `?page=1&per_page=20`, response includes `{ "data": [...], "pagination": { "page": 1, "per_page": 20, "total": 150 } }`
- Auth: Bearer token in Authorization header
- File uploads: multipart/form-data
- Dates: ISO 8601 format

### Key Endpoints

```
# Auth
POST   /api/v1/auth/player/otp/send     # Send OTP to phone
POST   /api/v1/auth/player/otp/verify    # Verify OTP, return JWT
POST   /api/v1/auth/coach/login          # Email/password login
POST   /api/v1/auth/refresh              # Refresh JWT token

# Players
GET    /api/v1/players                   # List players (coach/admin)
GET    /api/v1/players/:id               # Player profile
PUT    /api/v1/players/:id               # Update player info
GET    /api/v1/players/:id/progress      # Progress over time

# Videos
POST   /api/v1/videos/upload             # Upload video (returns video_id)
GET    /api/v1/videos/:id                # Video details + frames + feedback
GET    /api/v1/videos/:id/status         # Processing status (for polling)
GET    /api/v1/players/:id/videos        # Player's video history

# Frames
GET    /api/v1/videos/:id/frames         # All frames for a video (returns all 3 S3 URLs per frame)
GET    /api/v1/frames/:id                # Single frame detail with all view mode URLs + angles
PUT    /api/v1/frames/:id/reference      # Mark/unmark as reference (coach only)
GET    /api/v1/players/:id/references    # All reference frames for a player

# Feedback
GET    /api/v1/videos/:id/feedback       # All feedback for a video
POST   /api/v1/videos/:id/feedback       # Coach adds feedback
PUT    /api/v1/feedback/:id              # Update feedback
GET    /api/v1/players/:id/feedback      # Player's feedback history

# Coach Dashboard
GET    /api/v1/coach/queue               # Videos pending review
GET    /api/v1/coach/players             # Coach's assigned players
GET    /api/v1/coach/stats               # Review stats

# Admin
GET    /api/v1/admin/academy/stats       # Academy-wide usage
POST   /api/v1/admin/coaches             # Add coach
POST   /api/v1/admin/players             # Add player
```

---

## Coding Conventions

### Python (Backend)

- Use `async def` for all route handlers
- Type hints everywhere — function args and return types
- Use Pydantic models for all request/response schemas
- One file per model, one file per route group, one file per service
- Environment variables via `pydantic-settings` (never hardcode secrets)
- Logging with `structlog` (structured JSON logs)
- All database queries via SQLAlchemy async (not raw SQL)
- Tests with pytest + httpx for API tests
- Docstrings on all service functions explaining what they do

### JavaScript/TypeScript (Frontend)

**TypeScript:**

- TypeScript strict mode everywhere — no `any` types except in truly unavoidable edge cases
- All API responses and request payloads must have defined types in `api/types.ts`
- Use `interface` for object shapes, `type` for unions/intersections
- Prefer `const` assertions and discriminated unions over loose string types

**Components (shadcn/ui):**

- Use shadcn/ui as the primary component library — install components via `npx shadcn@latest add <component>`
- shadcn components live in `src/components/ui/` and are customizable (they're just code, not a dependency)
- Build app-specific components by composing shadcn primitives (Button, Card, Dialog, Sheet, Tabs, Badge, Tooltip, etc.)
- Use Radix UI primitives directly only when shadcn doesn't have the component you need
- Functional components only, no class components

**Forms (React Hook Form + Zod):**

- Every form uses React Hook Form with a Zod schema for validation
- Schemas live in `src/schemas/` (e.g., `feedback-schema.ts`, `player-schema.ts`)
- Always use the `zodResolver` — no manual validation logic
- Pattern:

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  feedbackSchema,
  type FeedbackFormData,
} from "@/schemas/feedback-schema";

const form = useForm<FeedbackFormData>({
  resolver: zodResolver(feedbackSchema),
  defaultValues: { note: "", drills: [] },
});
```

- Use shadcn's `<Form>`, `<FormField>`, `<FormItem>`, `<FormLabel>`, `<FormMessage>` wrappers for consistent form UI
- Never use uncontrolled inputs or manual `onChange` handlers for forms — let RHF handle it

**Server State (TanStack Query):**

- All API data fetching goes through TanStack Query hooks — never use `useEffect` + `useState` for API calls
- Wrap queries in custom hooks in `src/hooks/` (e.g., `usePlayer.ts`, `useVideoFrames.ts`)
- Pattern:

```tsx
// hooks/use-player.ts
import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import type { Player } from "@/api/types";

export function usePlayer(playerId: string) {
  return useQuery({
    queryKey: ["player", playerId],
    queryFn: () =>
      api.get<Player>(`/api/v1/players/${playerId}`).then((r) => r.data),
  });
}
```

- Use `useMutation` for all POST/PUT/DELETE operations with `onSuccess` invalidation
- Use optimistic updates for coach feedback submission (feels instant)
- Configure staleTime appropriately: 30s for video status polling, 5min for player profiles, 0 for coach queue

**Client State (Zustand):**

- Use Zustand only for client-side UI state that doesn't come from the API (e.g., selected view mode, sidebar open/closed, current phase selected)
- Keep stores small and focused — one store per concern (auth-store, ui-store)
- Never duplicate server state in Zustand — that's TanStack Query's job
- Pattern:

```tsx
// stores/ui-store.ts
import { create } from "zustand";

interface UIStore {
  viewMode: "raw" | "overlay" | "skeleton";
  setViewMode: (mode: "raw" | "overlay" | "skeleton") => void;
  selectedPhase: number;
  setSelectedPhase: (phase: number) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  viewMode: "raw",
  setViewMode: (mode) => set({ viewMode: mode }),
  selectedPhase: 0,
  setSelectedPhase: (phase) => set({ selectedPhase: phase }),
}));
```

**Styling (Tailwind CSS):**

- Tailwind CSS for all styling — no CSS modules, no styled-components, no inline styles
- Use the `cn()` utility (from shadcn) for conditional class merging:

```tsx
import { cn } from "@/lib/utils";
<div
  className={cn(
    "rounded-lg border",
    isActive && "border-green-500 bg-green-500/10",
  )}
/>;
```

- Follow shadcn's color convention: use CSS variables (`--primary`, `--muted`, etc.) configured in Tailwind
- Dark theme by default (matches our app design — dark green golf aesthetic)

**HTTP Client (Axios):**

- Single Axios instance in `api/client.ts` with auth interceptor that attaches JWT
- Response interceptor that handles 401 (redirect to login) and network errors
- All API calls go through this instance — never use raw `fetch()`
- Type the responses:

```tsx
// api/client.ts
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = getAuthToken(); // from auth store or secure storage
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

**Routing:**

- Coach dashboard: React Router v6 with lazy-loaded routes
- Player app: Expo Router (file-based routing in `app/` directory)

**Key shadcn Components We'll Use Heavily:**

- `Card`, `CardHeader`, `CardContent` — for swing cards, feedback cards, player cards
- `Dialog` / `Sheet` — for drill details, player profile modals
- `Tabs` — for phase selection, view mode toggling on desktop
- `Badge` — for score badges, status indicators (ok/minor/major)
- `Button` — all CTAs, toggle buttons
- `Form` + `Input` + `Textarea` — coach feedback forms
- `Tooltip` — angle explanations on hover
- `ScrollArea` — scrollable lists (coach queue, swing history)
- `Separator` — visual dividers
- `Skeleton` — loading states while frames/data load
- `Toast` — notifications (feedback sent, video processed)

**What NOT to Install:**

- No Material UI / Chakra UI / Ant Design — shadcn is the component system
- No Redux / MobX — Zustand + TanStack Query cover everything
- No Formik / Yup — React Hook Form + Zod is the standard
- No styled-components / Emotion — Tailwind only
- No moment.js — use `date-fns` if date formatting needed

### Naming

- Files: snake_case for Python, kebab-case for JS/TS
- Variables: snake_case for Python, camelCase for JS/TS
- Database tables: snake_case plural (players, videos, frames)
- API endpoints: kebab-case plural (/api/v1/videos)
- React components: PascalCase (SwingViewer, FrameComparison)

### Linting & Formatting

**Python (Ruff):**

- Use Ruff for both linting and formatting — it replaces flake8, isort, and black
- Config in `backend/pyproject.toml`:

```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM", "ASYNC"]
# E = pycodestyle, F = pyflakes, I = isort, N = naming,
# UP = pyupgrade, B = bugbear, SIM = simplify, ASYNC = async rules

[tool.ruff.format]
quote-style = "double"
```

- Run `ruff check .` and `ruff format .` before every commit
- All code must pass `ruff check` with zero errors

**TypeScript (ESLint + Prettier):**

- ESLint with `@typescript-eslint` for linting
- Prettier for formatting (single quotes, trailing commas, 100 char line width)
- Config in each frontend project's `eslint.config.js` and `.prettierrc`
- Run `npm run lint` and `npm run format` before every commit

**Pre-commit (enforce on every commit):**

- Install `pre-commit` (Python tool) in the repo root
- `.pre-commit-config.yaml` runs: ruff check, ruff format, eslint, prettier
- Every developer must run `pre-commit install` after cloning

### Error Handling

**Backend — Service Layer Pattern:**

- Services raise custom exceptions, API layer catches and returns proper HTTP responses
- Define exceptions in `backend/app/utils/exceptions.py`:

```python
class SwingLensError(Exception):
    """Base exception for all app errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code

class VideoProcessingError(SwingLensError):
    """Raised when video pipeline fails at any step."""
    pass

class PoseEstimationError(SwingLensError):
    """Raised when MediaPipe can't detect a pose reliably."""
    pass

class StorageError(SwingLensError):
    """Raised when S3 upload/download fails."""
    pass

class NotFoundError(SwingLensError):
    """Raised when a requested resource doesn't exist."""
    pass

class AuthError(SwingLensError):
    """Raised for auth failures."""
    pass
```

- Register a global exception handler in FastAPI:

```python
@app.exception_handler(SwingLensError)
async def swinglens_error_handler(request, exc):
    status_map = {
        NotFoundError: 404,
        AuthError: 401,
        VideoProcessingError: 422,
    }
    status = status_map.get(type(exc), 500)
    return JSONResponse(status_code=status, content={"error": {"message": exc.message, "code": exc.code}})
```

- Never let raw Python exceptions leak to the API response — always catch and wrap
- In Celery tasks: catch all exceptions, set video status='error' with the message, log the full traceback

**Backend — Pipeline Error Recovery:**

- If any step in the video pipeline fails, set `video.status = 'error'` and `video.error_message = str(error)`
- Clean up partial artifacts (delete temp files, any partial S3 uploads)
- Log the full error with structlog including video_id, step name, and traceback
- The player sees a friendly error message, not a stack trace

**Frontend — Error Handling:**

- TanStack Query handles retries automatically (3 retries with exponential backoff for network errors)
- Use TanStack Query's `onError` callbacks for mutations to show toast notifications
- Global axios response interceptor: 401 → redirect to login, 500 → show generic error toast
- All API errors display via shadcn Toast component — never silent failures

### Logging

**Backend (structlog):**

- Use structured JSON logging everywhere — never `print()`
- Log at appropriate levels:
  - `INFO`: Request received, video processing started/completed, feedback submitted
  - `WARNING`: Pose estimation low confidence, video validation failed, S3 retry
  - `ERROR`: Pipeline failure, S3 failure, Claude API failure, unexpected exceptions
- Always include context: `video_id`, `player_id`, `step_name`, `duration_ms`
- Pattern:

```python
import structlog
logger = structlog.get_logger()

logger.info("video_processing_started", video_id=str(video.id), player_id=str(video.player_id))
logger.error("pose_estimation_failed", video_id=str(video.id), step="pose_estimation", error=str(e))
```

- Never log sensitive data (tokens, passwords, full S3 keys)

---

## Video Processing Pipeline

This is the core of the product. When a player uploads a video, this pipeline runs asynchronously via Celery.

### Pipeline Steps

```
1. UPLOAD
   - Player uploads video from React Native app
   - Video saved to S3 under: /{academy_id}/{player_id}/{video_id}.mp4
   - Video record created in DB with status='processing'
   - Celery task queued

2. VALIDATE
   - Check video duration (must be 1-8 seconds for a single swing)
   - Check resolution (minimum 720p)
   - Detect camera angle (DTL vs face-on) using pose landmark positions
   - If invalid, set status='error' with message, notify player

3. EXTRACT FRAMES
   - Use ffmpeg to extract all frames at native FPS (typically 30-60fps for phone video, 120-240fps for slo-mo)
   - Store frame count and FPS in video record

4. POSE ESTIMATION
   - Run MediaPipe Pose on every frame
   - Store 33 landmarks per frame (x, y, z, visibility)
   - Filter frames where pose confidence is below 0.7

5. SWING PHASE DETECTION
   - Track lead wrist Y-position over time (primary signal)
   - Track shoulder rotation angle over time (secondary signal)
   - Detect swing phases using the algorithm below
   - Extract one canonical frame per phase

6. ANGLE CALCULATION
   - For each canonical frame, compute all tracked joint angles
   - See "Golf-Specific Joint Angles" section below

7. COMPARISON (if player has reference frames)
   - Load player's reference frames for each phase
   - Compute angle deltas between current and reference
   - Calculate severity: <5° = ok, 5-15° = minor, >15° = major
   - Generate overall similarity score (0-100)

8. ANNOTATION (Generate 3 view modes per frame — see "Frame View Modes" section)
   - RAW: Save the raw extracted frame as-is to S3 (s3_key_raw)
   - OVERLAY: Draw pose skeleton + angle measurements + deviation markers ON TOP of the raw photo frame
     - Color-code: green (ok), yellow (minor deviation), red (major deviation)
     - Draw comparison lines where deviations exist
     - Save to S3 (s3_key_overlay)
   - SKELETON: Render pose skeleton + angles on a clean dark background (#0a0f0d), no photo
     - Same color coding as overlay mode
     - Useful for clean side-by-side comparison when backgrounds differ
     - Save to S3 (s3_key_skeleton)
   - All 3 versions use identical annotation positions/colors so toggling feels seamless

9. AI FEEDBACK
   - Send annotated current frame + reference frame (if exists) to Claude Vision
   - Include joint angle data and deviation scores in prompt
   - Include player's skill level and dominant hand
   - Receive natural language coaching feedback
   - Save to comparison record

10. NOTIFY
    - Set video status='analyzed'
    - Push notification to player: "Your swing analysis is ready"
    - Add to coach's review queue
```

### Swing Phase Detection Algorithm

The golf swing is detected using the P Classification System adapted for 2D video analysis. We track 8 phases:

```python
SWING_PHASES = [
    "address",             # P1: Setup position, static before movement begins
    "takeaway",            # P2: Club parallel to ground in backswing
    "mid_backswing",       # P3: Lead arm parallel to ground
    "top",                 # P4: Top of backswing — maximum wrist height, max shoulder rotation
    "mid_downswing",       # P5-P6: Club returning, approaching horizontal
    "impact",              # P7: Club contacts ball — minimum wrist height during downswing
    "mid_follow_through",  # P8: Lead arm parallel to ground after impact
    "finish"               # P9-P10: Swing complete, body facing target
]
```

**Detection logic (using lead wrist Y-position trajectory):**

```
1. Smooth the wrist Y-position signal (moving average, window=5 frames)
2. Compute velocity (first derivative) and acceleration (second derivative)
3. Find the global minimum of wrist Y in the first half → this is ADDRESS
4. Find the global maximum of wrist Y → this is TOP
5. Find the global minimum of wrist Y after TOP → this is IMPACT
6. TAKEAWAY = point where wrist Y velocity first exceeds threshold after ADDRESS
7. MID_BACKSWING = midpoint between TAKEAWAY and TOP (by wrist height)
8. MID_DOWNSWING = midpoint between TOP and IMPACT (by wrist height)
9. MID_FOLLOW_THROUGH = point where wrist Y re-reaches mid_backswing height after IMPACT
10. FINISH = last frame where pose is detected with high confidence
```

**Important:** For face-on camera angle, use lead wrist X-position instead of Y for horizontal tracking. The detection logic adapts based on detected camera angle.

---

## Golf Domain Knowledge

This section is critical. The AI must understand golf to give useful feedback. Every developer working on this project should read this section.

### The 8 Swing Phases and What to Check

#### 1. ADDRESS (Setup)

**What it is:** The starting position before the swing begins.
**Key checkpoints:**

- Feet shoulder-width apart (wider for driver, narrower for wedges)
- Weight distribution: 50-50 for irons, 55-45 (trail foot heavier) for driver
- Spine tilt: slight tilt away from target (right shoulder lower for right-handed player)
- Knee flex: ~20-25° bend
- Hip hinge: ~35-45° forward bend at hips
- Arms hanging naturally, hands below chin
- Ball position: front heel for driver, center for mid-irons, slightly back for wedges

**Common faults:** Slouching (too much spine curve), too wide/narrow stance, weight too far forward or back, arms reaching too far from body.

**Angles to measure:**

- `spine_angle`: Angle of spine relative to vertical (should be ~35-45°)
- `knee_flex`: Angle at knee joint (~155-165°, i.e., ~20-25° of bend)
- `hip_hinge`: Angle at hip joint
- `shoulder_tilt`: Difference in shoulder height (slight trail-side drop)

#### 2. TAKEAWAY

**What it is:** The first movement — club moves back until shaft is parallel to the ground.
**Key checkpoints:**

- Club head should "hide" the hands when viewed from down-the-line
- Lead arm and club form a relatively straight line
- Minimal wrist hinge at this point
- Lower body is quiet — rotation hasn't started significantly
- Triangle formed by shoulders and arms maintained

**Common faults:** Rolling the club inside (too flat), picking it up (too steep), excessive wrist hinge too early, swaying hips laterally instead of staying centered.

**Angles to measure:**

- `lead_arm_angle`: Angle of lead arm relative to ground
- `wrist_hinge`: Angle at lead wrist (should still be minimal)
- `hip_sway`: Lateral displacement of hips from address (should be minimal)

#### 3. MID-BACKSWING

**What it is:** Lead arm is parallel to the ground going back.
**Key checkpoints:**

- Wrists begin natural hinge
- Club should be "on plane" — club roughly points at the target line
- Shoulders beginning to rotate, ~45° turned
- Weight starting to shift to trail foot
- Head stays relatively still

**Common faults:** Club too far inside or outside the plane, over-rotation of forearms, head moving laterally.

**Angles to measure:**

- `shoulder_rotation`: Rotation of shoulders from address (~45° here)
- `hip_rotation`: Rotation of hips from address (~20-25° here)
- `lead_arm_to_ground`: Should be approximately parallel (0° relative to ground)

#### 4. TOP (Most Critical Checkpoint #1)

**What it is:** The top of the backswing — maximum coil position.
**Key checkpoints:**

- Shoulders rotated ~90-100° from address
- Hips rotated ~45° from address (this creates the "X-factor" — the differential between hip and shoulder rotation, which is the key power source)
- Lead arm relatively straight (slight bend OK)
- Lead wrist flat or slightly bowed (NOT cupped/extended — cupped wrist opens the clubface)
- Club shaft approximately parallel to ground (not past parallel = overswing)
- Weight ~60-70% on trail foot
- Spine angle maintained from address (no standing up)
- Head position hasn't moved significantly from address

**Common faults:** Overswing (past parallel), cupped lead wrist (opens face), reverse pivot (weight on lead foot), loss of spine angle (standing up), laid off (club points left of target) or across the line (club points right).

**Angles to measure:**

- `shoulder_rotation`: ~90-100° from address
- `hip_rotation`: ~40-50° from address
- `x_factor`: shoulder_rotation - hip_rotation (should be ~45-55°)
- `lead_arm_straightness`: Angle at lead elbow (should be >160°, ideally straight)
- `spine_angle`: Should match address spine angle (±5°)
- `trail_knee_flex`: Should maintain flex from address (not straighten)

#### 5. MID-DOWNSWING

**What it is:** The transition — club coming down, approximately horizontal.
**Key checkpoints:**

- CRITICAL: Downswing MUST be initiated by lower body (hips start rotating toward target BEFORE shoulders)
- Hips "bump" slightly toward target then rotate open
- Club "drops" into the slot (shallows, approaches from inside)
- Lag retained — angle between lead arm and club shaft is acute
- Weight shifting aggressively to lead foot

**Common faults:** "Over the top" (shoulders fire first, club comes from outside), casting (releasing lag too early by straightening wrists), hanging back (weight stays on trail foot), early extension (hips thrust toward ball instead of rotating).

**Angles to measure:**

- `hip_rotation`: Should be 20-30° OPEN to target (ahead of shoulders)
- `shoulder_rotation`: Should still be relatively square or slightly open
- `lag_angle`: Angle between lead forearm and club shaft (smaller = more lag = more power)
- `hip_sway_forward`: Weight shift toward target

#### 6. IMPACT (Most Critical Checkpoint #2)

**What it is:** The moment the club contacts the ball.
**Key checkpoints:**

- Hips ~40-45° open to target
- Shoulders approximately square to slightly open
- Lead wrist flat or slightly bowed (forward shaft lean)
- Hands ahead of the club head (forward shaft lean for irons)
- Weight ~80% on lead foot
- Head behind the ball (for driver especially)
- Lead arm and club shaft form a roughly straight line (from face-on view)
- Spine angle maintained

**Common faults:** Flipping/scooping (hands behind club head, wrists break down), hanging back, early extension, loss of posture, open or closed clubface.

**Angles to measure:**

- `hip_rotation`: ~40-45° open
- `shoulder_rotation`: ~0-20° open
- `hip_shoulder_gap`: Hips still leading shoulders
- `spine_angle`: Should match address (±5°) — loss indicates early extension
- `lead_arm_angle`: Relationship of lead arm to shaft
- `forward_shaft_lean`: Hands ahead of club head (positive = good for irons)
- `weight_distribution`: Estimated from hip/knee positions (~80% lead foot)

#### 7. MID-FOLLOW-THROUGH

**What it is:** After impact, lead arm returns to parallel with ground.
**Key checkpoints:**

- Full release — club head has passed hands
- Both arms extending toward target
- Body continuing to rotate
- Weight almost entirely on lead foot
- Trail heel lifting off ground

**Common faults:** "Chicken wing" (lead elbow folds), blocking (body stops rotating), deceleration.

**Angles to measure:**

- `lead_elbow_fold`: Lead arm should still be relatively extended (no chicken wing)
- `hip_rotation`: Continuing toward target (~60-70° open)
- `spine_angle`: Beginning to straighten is acceptable

#### 8. FINISH

**What it is:** The completed swing position.
**Key checkpoints:**

- Chest facing target (or slightly left of target for right-handed player)
- Weight ~95% on lead foot
- Trail foot up on toe only
- Balanced — can hold this position for 3 seconds
- Club wrapped around behind shoulders
- Hips fully rotated (~90° from address)

**Common faults:** Falling off balance (indicates issues earlier in swing), not completing rotation, weight still on trail foot.

**Angles to measure:**

- `hip_rotation`: ~80-90° open (fully rotated)
- `chest_orientation`: Facing target
- `balance`: Hip position over lead foot (centered = balanced)
- `trail_foot`: Only toe touching ground

### MediaPipe Landmark IDs for Golf

```python
# MediaPipe Pose provides 33 landmarks. Key ones for golf:
LANDMARKS = {
    # Head
    "nose": 0,
    "left_ear": 7,
    "right_ear": 8,

    # Shoulders
    "left_shoulder": 11,
    "right_shoulder": 12,

    # Elbows
    "left_elbow": 13,
    "right_elbow": 14,

    # Wrists
    "left_wrist": 15,
    "right_wrist": 16,

    # Hips
    "left_hip": 23,
    "right_hip": 24,

    # Knees
    "left_knee": 25,
    "right_knee": 26,

    # Ankles
    "left_ankle": 27,
    "right_ankle": 28,
}

# For a RIGHT-HANDED golfer (facing right in DTL view):
#   Lead side = LEFT (closer to target)
#   Trail side = RIGHT (farther from target)
# For a LEFT-HANDED golfer, swap these.

# Key angle calculations:
def calc_angle(a, b, c):
    """Angle at point B formed by points A-B-C, in degrees."""
    import math
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    cos_angle = (ba[0]*bc[0] + ba[1]*bc[1]) / (
        math.sqrt(ba[0]**2 + ba[1]**2) * math.sqrt(bc[0]**2 + bc[1]**2) + 1e-6
    )
    return math.degrees(math.acos(max(-1, min(1, cos_angle))))

# GOLF-SPECIFIC ANGLES TO COMPUTE PER FRAME:
GOLF_ANGLES = {
    "spine_angle": ("mid_hip", "mid_shoulder", "vertical_ref"),
    "knee_flex_lead": ("left_hip", "left_knee", "left_ankle"),
    "knee_flex_trail": ("right_hip", "right_knee", "right_ankle"),
    "hip_hinge": ("left_knee", "left_hip", "left_shoulder"),
    "lead_elbow": ("left_shoulder", "left_elbow", "left_wrist"),
    "trail_elbow": ("right_shoulder", "right_elbow", "right_wrist"),
    "shoulder_rotation": "computed_from_shoulder_line_vs_camera",
    "hip_rotation": "computed_from_hip_line_vs_camera",
    "lead_arm_angle": ("left_shoulder", "left_wrist", "ground_ref"),
}
```

### Deviation Severity Thresholds

```python
# How far off from reference is acceptable
SEVERITY_THRESHOLDS = {
    "ok": 5,        # Within 5° of reference = looks good
    "minor": 15,    # 5-15° off = worth noting but not alarming
    "major": 15,    # >15° off = significant issue to address
}

# Some angles matter more than others. Weight them for overall score.
ANGLE_WEIGHTS = {
    "spine_angle": 1.5,         # Maintaining spine angle is critical
    "x_factor": 1.5,            # Power differential
    "hip_rotation": 1.3,        # Sequence matters
    "shoulder_rotation": 1.2,
    "lead_elbow": 1.0,
    "knee_flex_lead": 0.8,
    "knee_flex_trail": 0.8,
}
```

### Camera Angle Detection

```python
# Detect if video is DTL (down-the-line) or face-on
# DTL: Camera behind player, both shoulders roughly same X position
# Face-on: Camera facing player, shoulders spread wide in X

def detect_camera_angle(landmarks):
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    shoulder_x_diff = abs(left_shoulder.x - right_shoulder.x)
    shoulder_z_diff = abs(left_shoulder.z - right_shoulder.z)

    # If shoulders are spread wide horizontally = face-on
    # If shoulders are close horizontally = down-the-line
    if shoulder_x_diff > 0.15:
        return "face_on"
    else:
        return "dtl"
```

### Camera Setup Requirements (Show to Player in App)

**Down-the-Line (DTL):**

- Position camera directly behind the player, aligned with target line
- Camera at hand/belt height
- Player should fill ~60-70% of frame height
- At least 3 feet of space visible above player's head for club at top

**Face-On:**

- Position camera directly facing the player
- Camera at hand/belt height
- Player centered in frame
- Full body visible including feet and space above head

---

## Claude API Prompts

These prompts live in `/prompts/` and are loaded by `ai_feedback.py`. Variables are injected using `{variable_name}` syntax.

### Prompt: Swing Analysis (swing_analysis.txt)

```
You are an expert golf coach analyzing a player's swing. You are warm, encouraging, and specific in your feedback. You focus on the most impactful 2-3 things the player should work on, not everything at once.

Player Profile:
- Skill level: {skill_level}
- Handicap: {handicap}
- Dominant hand: {dominant_hand}
- Club used: {club_type}

Camera angle: {camera_angle}

You are looking at a frame from the {swing_phase} phase of the swing.

Measured joint angles:
{joint_angles_formatted}

{comparison_section}

Analyze this frame and provide:
1. POSITION ASSESSMENT: Is this a good position for this phase? What looks solid?
2. KEY ISSUE (if any): What is the single most important thing to improve? Be specific — reference body parts and angles. Explain WHY this matters for their ball flight.
3. FEEL CUE: Give one simple feel or mental image the player can use on their next swing to improve this position. Golfers respond best to feels, not mechanical thoughts.

Keep your response under 150 words. Use simple language. No jargon without explanation. Be encouraging — always start with what's working before addressing what to fix.
```

### Prompt: Baseline Comparison (baseline_comparison.txt)

```
You are an expert golf coach comparing a player's current swing to their own personal best.

Player Profile:
- Skill level: {skill_level}
- Dominant hand: {dominant_hand}

You are comparing the {swing_phase} phase.

Current swing angles:
{current_angles}

Personal best (reference) angles:
{reference_angles}

Deviations:
{deviations_formatted}

The images show the current swing (left) and their reference/best swing (right) at the same phase.

Provide:
1. What has stayed consistent (positive reinforcement)
2. The most significant deviation and what it likely means for ball flight
3. One drill or practice focus to get back to their reference position

Keep it under 120 words. Be specific and encouraging.
```

### Prompt: Progress Summary (progress_summary.txt)

```
You are an expert golf coach reviewing a player's progress over the past {time_period}.

Player Profile:
- Skill level: {skill_level}
- Handicap: {handicap}
- Total swings analyzed this period: {swing_count}

Trend data (average angles over the period):
{trend_data_formatted}

Consistency scores by phase:
{consistency_scores}

Top improvements:
{improvements}

Persistent issues:
{persistent_issues}

Write a brief progress report (under 200 words) that:
1. Celebrates what has improved
2. Identifies the one area that still needs the most attention
3. Suggests a practice plan focus for the next period
4. Encourages the player to keep going

Tone: Like a supportive coach who genuinely cares about the player's development.
```

---

## Annotation Visual Style

When drawing overlays on frames:

```python
ANNOTATION_STYLE = {
    # Pose skeleton
    "skeleton_color": (0, 255, 128),      # Green
    "skeleton_thickness": 2,
    "landmark_radius": 4,

    # Angle measurements
    "angle_font_scale": 0.5,
    "angle_ok_color": (0, 200, 0),         # Green
    "angle_minor_color": (0, 200, 255),    # Yellow/Orange
    "angle_major_color": (0, 0, 255),      # Red

    # Comparison lines (when showing deviation)
    "reference_line_color": (255, 200, 0),  # Cyan — "where you should be"
    "current_line_color": (0, 0, 255),      # Red — "where you are"
    "deviation_arc_color": (0, 100, 255),   # Orange arc showing the gap

    # Skeleton-only mode background
    "skeleton_bg_color": (10, 15, 13),     # Dark background matching app theme (#0a0f0d)
}
```

---

## Frame View Modes

Every extracted frame is stored in 3 versions. The frontend provides a toggle to switch between them. This is a core UX feature — coaches need the real photo, players benefit from the overlay, and skeleton-only enables clean comparison.

### The 3 Modes

| Mode         | What It Shows                                                | S3 Key            | When to Use                                                             |
| ------------ | ------------------------------------------------------------ | ----------------- | ----------------------------------------------------------------------- |
| **Raw**      | Actual photo frame from the video, no overlays               | `s3_key_raw`      | Default view. Coaches assess posture, grip, club position naturally.    |
| **Overlay**  | Photo frame + pose skeleton + angle annotations drawn on top | `s3_key_overlay`  | Power view. Real image with data layered in. Best of both worlds.       |
| **Skeleton** | Stick figure + angles on dark background, no photo           | `s3_key_skeleton` | Clean comparison when backgrounds differ between current and reference. |

### Frontend Toggle Behavior

**Player App (mobile):**

- Default view: **Raw** (the actual photo — this is what feels familiar)
- Single tap on frame: toggles to **Overlay** (photo + skeleton + angles)
- Tap again: back to **Raw**
- Skeleton-only mode NOT shown to players (too abstract, not useful for them)

**Coach Dashboard (desktop):**

- Default view: **Raw** (coaches want to see the real image first)
- Toggle bar with 3 buttons: Raw | Overlay | Skeleton
- Additional layer toggles (checkboxes) in Overlay mode:
  - ☑ Show skeleton
  - ☑ Show angles
  - ☑ Show deviation markers
  - ☑ Show reference position ghost (faded skeleton of reference pose overlaid)
- Both the current frame and reference frame switch view modes together (synced toggle)

### S3 Storage Structure Per Frame

```
/{academy_id}/{player_id}/{video_id}/frames/
  ├── {phase}_raw.jpg          # Raw photo frame
  ├── {phase}_overlay.jpg      # Photo + annotations
  └── {phase}_skeleton.png     # Skeleton on dark bg (PNG for transparency support)
```

### Frame API Response Shape

```json
{
  "id": "uuid",
  "video_id": "uuid",
  "swing_phase": "mid_downswing",
  "frame_number": 47,
  "images": {
    "raw": "https://cdn.swinglens.com/.../mid_downswing_raw.jpg",
    "overlay": "https://cdn.swinglens.com/.../mid_downswing_overlay.jpg",
    "skeleton": "https://cdn.swinglens.com/.../mid_downswing_skeleton.png"
  },
  "joint_angles": {
    "hip_rotation": 24.3,
    "shoulder_rotation": 12.1,
    "spine_angle": 38.7,
    "lag_angle": 72.0
  },
  "is_reference": false
}
```

### Annotator Service (backend/app/services/annotator.py)

The annotator generates all 3 versions from the same frame + keypoints data:

```python
def generate_frame_views(raw_frame, keypoints, joint_angles, deviations=None):
    """
    Generate all 3 view modes for a frame.

    Args:
        raw_frame: OpenCV image (BGR) — the raw extracted frame
        keypoints: dict of MediaPipe landmarks
        joint_angles: dict of computed angles
        deviations: optional dict of {angle: {delta, severity}} for color coding

    Returns:
        dict with keys 'raw', 'overlay', 'skeleton' — each an OpenCV image
    """
    # 1. Raw — just return as-is
    raw = raw_frame.copy()

    # 2. Overlay — draw on top of photo
    overlay = raw_frame.copy()
    draw_skeleton(overlay, keypoints)
    draw_angles(overlay, keypoints, joint_angles, deviations)
    if deviations:
        draw_deviation_markers(overlay, keypoints, deviations)

    # 3. Skeleton — draw on dark background
    h, w = raw_frame.shape[:2]
    skeleton_bg = np.full((h, w, 3), ANNOTATION_STYLE["skeleton_bg_color"], dtype=np.uint8)
    draw_skeleton(skeleton_bg, keypoints)
    draw_angles(skeleton_bg, keypoints, joint_angles, deviations)
    if deviations:
        draw_deviation_markers(skeleton_bg, keypoints, deviations)

    return {"raw": raw, "overlay": overlay, "skeleton": skeleton_bg}
```

### Reference Ghost Overlay (Coach-Only Feature)

When a coach is in Overlay mode and the player has a reference frame for the same phase, the coach can toggle a "ghost" overlay that shows the reference pose skeleton faintly on top of the current frame. This lets the coach see exactly where the player deviates without switching between two images.

```python
def draw_reference_ghost(frame, reference_keypoints, alpha=0.3):
    """Draw a faded reference skeleton on top of the current frame."""
    ghost_color = (200, 200, 0)  # Faded cyan
    draw_skeleton(frame, reference_keypoints, color=ghost_color, thickness=1, alpha=alpha)
```

This is rendered client-side in the coach dashboard using canvas or SVG overlay (not a separate S3 image) since we have the keypoints data in the API response.

---

## What NOT To Do

- **Never use raw SQL** — always SQLAlchemy
- **Never hardcode S3 credentials** — use environment variables
- **Never store video files locally** — always stream to/from S3
- **Never process video synchronously** in an API request — always use Celery
- **Never compare a player to a "generic ideal"** — always compare to their OWN reference frames
- **Never give negative-only feedback** — AI must always lead with something positive
- **Never show the AI feedback to the coach as "truth"** — frame it as "AI suggestion" that coach can approve/edit
- **Never skip the camera angle validation** — bad angles produce unreliable analysis
- **Never use class components in React** — functional only
- **Never use localStorage in React Native** — use Expo SecureStore for tokens
- **Never use `useEffect` + `useState` for API calls** — always use TanStack Query hooks
- **Never use `any` type in TypeScript** — define proper types, use `unknown` if truly unavoidable
- **Never install MUI, Chakra, Ant Design, or any other component library** — shadcn/ui is the standard
- **Never use Redux, MobX, or Context for server state** — TanStack Query handles that
- **Never write manual form validation** — always use React Hook Form + Zod
- **Never write raw CSS files** — Tailwind only, use `cn()` for conditional classes
- **Never use inline styles in the web app** — Tailwind classes only (inline styles are acceptable in React Native where Tailwind isn't native)
- **Never default to skeleton view** — always show the raw photo first. The real image is what coaches and players trust. Skeleton is an analytical tool, not the primary view.
- **Never show skeleton-only mode to players** — it's too abstract. Players get Raw and Overlay only. Coaches get all 3 modes.

---

## UX Principles

### For Players

- **Instant gratification:** Show something useful within 30 seconds of upload. Even if AI feedback is still generating, show the extracted frames with basic angle measurements immediately.
- **Real image first:** Default view is always the raw photo frame. Players want to see themselves, not a stick figure. The overlay toggle adds data when they want it.
- **One thing at a time:** AI feedback should focus on the single most impactful fix. Players are overwhelmed by 10 things to correct.
- **Progress is motivating:** Show trends over time. "Your spine angle consistency improved 12% this month" is powerful.
- **Camera guidance:** Make it brain-dead simple to set up the camera correctly. Overlay guide lines on the camera view.

### For Coaches

- **Save time, not replace judgment:** The system extracts and curates. The coach decides.
- **Quick review:** Coach should be able to review a submission in under 2 minutes (vs 10+ minutes watching full video). Show frames, show AI suggestion, one-click approve or override.
- **Full visual control:** Coach can toggle between raw photo, overlay, and skeleton views. They can toggle individual annotation layers on/off. They can overlay the reference ghost to see deviations in-place. Give them the tools, don't force a single view.
- **Never make the coach look wrong:** If AI feedback contradicts what the coach told the player, the coach's word wins. The system learns from coach corrections.
- **Batch workflow:** Coach reviews a queue, not one-at-a-time. Think email inbox, not chat.

---

## Build Order (Phases)

### Phase 1: Video Pipeline (8-10 sessions)

Goal: Upload a video, extract frames, run pose estimation, detect swing phases.
No comparison, no AI feedback yet. Just the raw pipeline.

### Phase 2: Coach Dashboard MVP (5-6 sessions)

Goal: Coach can log in, see player list, see uploaded videos, view extracted frames.
Basic review workflow — coach can add text notes.

### Phase 3: Player Profile & Comparison (5-7 sessions)

Goal: Coach can mark reference frames. System compares new swings against baseline.
Deviation scoring, annotated frames with angle overlays.

### Phase 4: AI Feedback Layer (3-4 sessions)

Goal: Claude Vision generates coaching feedback per swing.
Prompts from /prompts/ directory. Coach can approve/edit.

### Phase 5: Player Mobile App (5-7 sessions)

Goal: Player can upload video, see feedback, view history.
Camera guide overlay, push notifications.

### Phase 6: Progress & Polish (3-4 sessions)

Goal: Progress tracking, drill recommendations, polish UX, deploy.

**Total: ~30-38 sessions**

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/swinglens

# Redis (Celery broker)
REDIS_URL=redis://localhost:6379/0

# AWS S3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=swinglens-media
AWS_S3_REGION=ap-south-1

# Claude API
ANTHROPIC_API_KEY=

# JWT
JWT_SECRET_KEY=
JWT_EXPIRY_MINUTES=1440

# OTP (use MSG91 or similar for India)
OTP_API_KEY=
OTP_TEMPLATE_ID=

# Firebase (push notifications)
FIREBASE_CREDENTIALS_PATH=

# App
APP_ENV=development
API_BASE_URL=http://localhost:8000
```

---

## Testing Strategy

**Rule: Every session that builds a service or API endpoint must include tests for that session's work.** Tests are not a separate phase — they're part of the definition of done.

### Backend Testing (pytest + httpx)

**Structure:**

```
backend/tests/
├── conftest.py              # Shared fixtures: test DB, test client, auth helpers
├── test_auth.py             # Auth endpoints
├── test_players.py          # Player CRUD
├── test_videos.py           # Video upload + status
├── test_frames.py           # Frame endpoints
├── test_feedback.py         # Feedback endpoints
├── services/
│   ├── test_pose_estimator.py
│   ├── test_swing_detector.py
│   ├── test_angle_calculator.py
│   ├── test_comparator.py
│   ├── test_annotator.py
│   └── test_ai_feedback.py
└── fixtures/
    └── test_videos/         # 3-5 short golf swing clips for pipeline tests
```

**conftest.py must include:**

- An async test database (use a separate PostgreSQL DB: `swinglens_test`)
- A `test_client` fixture that provides an httpx AsyncClient pointed at the test app
- `auth_token_coach` and `auth_token_player` fixtures that return valid JWTs
- A `seed_data` fixture that creates a test academy, coach, and player

**What to test per layer:**

- **API endpoints:** Happy path (correct input → correct response), auth required (no token → 401), wrong role (player hitting coach endpoint → 403), validation (bad input → 422), not found (bad UUID → 404)
- **Services:** Unit test with known inputs. For angle_calculator, use hardcoded landmark positions where you can hand-calculate the expected angle. For swing_detector, use a synthetic wrist-Y trajectory where you know where the phases should be. For comparator, use known angle pairs and verify severity thresholds.
- **Pipeline:** Integration test that uploads a real test video and verifies the full pipeline produces frames, angles, and comparisons. This runs slower — mark with `@pytest.mark.slow`.

**Test commands:**

```bash
cd backend
pytest                        # run all tests
pytest -x                     # stop on first failure
pytest tests/test_auth.py     # run one file
pytest -m "not slow"          # skip slow pipeline tests
pytest --cov=app --cov-report=term-missing  # coverage report
```

**Coverage target:** 80%+ on `backend/app/services/` and `backend/app/api/`. Don't chase 100% — focus on the logic that matters.

### Frontend Testing (Vitest + Testing Library)

- Use Vitest (not Jest) for the coach dashboard — it integrates with Vite
- Use React Testing Library for component tests
- Test: form validation (Zod schemas reject bad input), API hook behavior (mock TanStack Query), critical user flows (coach can navigate queue, toggle view modes, submit feedback)
- Don't test shadcn component internals — they're already tested upstream
- Frontend test coverage is lower priority than backend — focus on the coach review flow and video upload flow

### Test Data

- Keep 3-5 short (2-3 second) golf swing test videos in `backend/tests/fixtures/test_videos/`
- Include: one good DTL swing, one face-on swing, one with obvious faults, one left-handed
- These videos are committed to the repo (they're small, <5MB each)
- Use them for pipeline integration tests and for manual QA

---

## Notes for Developers

1. **Read the Golf Domain Knowledge section above.** You must understand what each swing phase looks like and what angles matter before writing pose analysis code.

2. **When in doubt, ask Jai.** Architecture decisions, prompt tweaks, and golf domain questions go to Jai. Don't guess on these.

3. **Small commits.** One feature per commit. Clear commit messages: "Add frame extraction from video using ffmpeg" not "update stuff".

4. **Test before committing.** Run the feature manually. Does the endpoint return the right data? Does the frame look correct? Don't commit untested code.

5. **Keep Claude API prompts in /prompts/ directory.** Never hardcode prompts in Python files. Jai will refine these directly.
