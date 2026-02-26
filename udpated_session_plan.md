# SwingLens — Updated Session Plan

**What changed:** Linting/formatting setup added to Sessions 1c/1d. Per-session testing added to every session that builds services or APIs. Error handling patterns enforced from Session 2 onward. Session 33 repurposed from "write all tests" to "integration tests + coverage gaps only."

Sessions 1a and 1b are unchanged (already done/in progress).

---

## SESSION 1c — Coach Dashboard Scaffolding (You)

```
Set up the coach dashboard in coach-dashboard/ using Vite + React + TypeScript (strict mode). Initialize shadcn/ui with the dark theme and the green color palette (primary: emerald/green to match our golf theme). Install and configure: @tanstack/react-query v5, react-router-dom v6, zustand, react-hook-form, @hookform/resolvers, zod, axios. Create the folder structure from CLAUDE.md including components/ui/, schemas/, stores/, api/, hooks/, lib/utils.ts with cn() helper. Set up the Axios client in api/client.ts with a request interceptor that attaches Bearer token from auth store. Set up QueryClientProvider and BrowserRouter in main.tsx. Create a placeholder route at / that renders a shadcn Card with dark background saying "SwingLens Coach Dashboard". npm run dev should work on port 5173.

ALSO: Set up ESLint with @typescript-eslint and Prettier. Add eslint.config.js and .prettierrc (single quotes, trailing commas, 100 char line width). Add npm scripts: "lint": "eslint src/", "format": "prettier --write src/". Add Vitest + @testing-library/react for testing. Add npm script: "test": "vitest run". Verify npm run lint and npm run test both pass.
```

---

## SESSION 1d — Player App Scaffolding (You)

```
Set up the player app in player-app/ using Expo with TypeScript and Expo Router (file-based routing). Install: @tanstack/react-query, zustand, react-hook-form, @hookform/resolvers, zod, axios, expo-secure-store, expo-camera, expo-file-system. Create the folder structure from CLAUDE.md including api/, schemas/, stores/, hooks/. Set up Axios client in api/client.ts with auth interceptor that reads token from expo-secure-store. Set up QueryClientProvider in app/_layout.tsx. Create a home tab screen that displays "SwingLens" with a green accent. npx expo start should work.

ALSO: Set up ESLint with @typescript-eslint and Prettier using the same config as coach-dashboard. Add lint and format scripts to package.json.
```

After 1c and 1d: Set up pre-commit hooks in the repo root using `pre-commit` (Python tool). Create `.pre-commit-config.yaml` that runs: ruff check + ruff format for backend, eslint + prettier for coach-dashboard and player-app. Commit the config. Every developer must run `pre-commit install` after cloning.

---

## SESSION 2: Auth System (Developer)

**Task 2a:**

```
Build JWT auth utilities in backend/app/utils/auth.py. Create functions: create_access_token(user_id, role) that returns a JWT with 24hr expiry, and verify_token(token) that returns the payload. Create a FastAPI dependency get_current_user() that extracts and verifies the Bearer token from the Authorization header and returns {user_id, role}. Create a require_role(role) dependency that checks the user's role. Use python-jose for JWT and the JWT_SECRET_KEY from config.

Write tests in backend/tests/test_auth.py: test token creation and verification, test expired token rejection, test invalid token rejection, test get_current_user dependency with valid/missing/bad tokens.
```

**Task 2b:**

```
Build player auth endpoints. POST /api/v1/auth/player/otp/send accepts {phone} and returns {success: true}. In development mode (APP_ENV=development), always use OTP 123456 — don't actually send an SMS. Store the OTP in Redis with a 5 minute TTL. POST /api/v1/auth/player/otp/verify accepts {phone, otp}, validates against Redis, and returns {token, player} with a JWT. If the player doesn't exist yet, auto-create them with the phone number.

Use the custom exception classes from CLAUDE.md (AuthError for bad OTP, etc.). Write tests: valid OTP flow, expired OTP, wrong OTP, auto-create new player on first verify.
```

**Task 2c:**

```
Build coach auth endpoints. POST /api/v1/auth/coach/login accepts {email, password}, verifies with bcrypt, and returns {token, coach}. Create a seed script at backend/scripts/seed.py that creates a test academy "TSG Bangalore", a test coach (email: coach@tsg.com, password: test1234), and 3 test players assigned to that coach. Run it.

Write tests: valid coach login, wrong password (AuthError), non-existent email (NotFoundError).
```

---

## SESSION 3: Player & Coach CRUD (Developer)

**Task 3a:**

```
Build player endpoints. GET /api/v1/players returns paginated player list (coach sees only their assigned players, admin sees all). GET /api/v1/players/:id returns full player profile. PUT /api/v1/players/:id updates player info (name, handicap, skill_level, dominant_hand). All endpoints require auth. Use Pydantic schemas for request/response in backend/app/schemas/player.py. Follow the pagination format from CLAUDE.md.

Write tests: list players as coach (sees only assigned), get player by ID, update player, 401 without token, 403 when coach accesses unassigned player, 404 for bad UUID.
```

**Task 3b:**

```
Build coach endpoints. GET /api/v1/coach/players returns the coach's assigned players with their latest video status and swing count. GET /api/v1/coach/queue returns videos with status='analyzed' for the coach's players, ordered by most recent first. GET /api/v1/coach/stats returns: total_players, pending_reviews, reviews_this_week.

Write tests: coach/players returns correct list, coach/queue returns only analyzed videos for assigned players, coach/stats returns correct counts.
```

---

## SESSION 4: S3 Storage & Video Upload (Developer)

**Task 4a:**

```
Build the S3 storage service in backend/app/services/storage.py. Create functions: upload_file(file_bytes, s3_key) -> s3_url, generate_presigned_url(s3_key, expiry=3600) -> url, delete_file(s3_key). Use boto3 async. All frame and video URLs returned by the API should be presigned URLs (not raw S3 keys). For development, use MinIO as an S3-compatible local store — add it to docker-compose.yml on port 9000.

Raise StorageError (from CLAUDE.md exceptions) on any S3 failure. Write tests: upload and retrieve a file from MinIO, generate presigned URL, handle missing file (StorageError).
```

**Task 4b:**

```
Build POST /api/v1/videos/upload. Accept multipart form data with fields: file (mp4), camera_angle (optional, "dtl" or "face_on"), club_type (optional). Validate: file must be mp4 or mov, max 50MB. Upload to S3 under /{academy_id}/{player_id}/{video_id}.mp4. Create a video record with status='uploading', then update to 'processing'. Queue a Celery task process_video(video_id). Return {video_id, status}. Also build GET /api/v1/videos/:id/status that returns the current processing status (for polling).

Write tests: upload valid mp4, reject >50MB file (422), reject non-mp4 (422), status polling returns correct status.
```

---

## SESSION 5: Celery Pipeline Part 1 — Frame Extraction (Developer)

```
Set up Celery in backend/app/tasks/. Create the Celery app configuration in backend/app/celery_app.py using Redis as broker. Create the process_video task in backend/app/tasks/process_video.py. For now, implement only steps 1-3 of the pipeline from CLAUDE.md:

1. Download the video from S3 to a temp file
2. VALIDATE: Check duration is 1-20 seconds using ffprobe. Check resolution is at least 720p. If invalid, set video status='error' with a message.
3. EXTRACT FRAMES: Use ffmpeg to extract all frames at the video's native FPS. Store frame count and FPS in the video record.

Save extracted frames as /tmp/{video_id}/frame_{number}.jpg. Update video status to 'processing'. Log each step with structlog (include video_id and step name). On any failure, set status='error' with error message and clean up temp files.

Write tests: mock S3 download, test validation rejects <1s and >8s videos, test validation rejects <720p, test frame extraction produces expected count. Mark pipeline tests with @pytest.mark.slow.
```

---

## SESSION 6: Celery Pipeline Part 2 — Pose Estimation (You)

```
Add step 4 (POSE ESTIMATION) to the process_video task. Create backend/app/services/pose_estimator.py. Use MediaPipe Pose to process each extracted frame. For each frame, extract all 33 landmarks with x, y, z, and visibility. Filter out frames where the average landmark visibility is below 0.7. Store the results as a list of dicts: [{frame_number, landmarks: {landmark_id: {x, y, z, visibility}}}]. Raise PoseEstimationError if no frames pass the visibility threshold.

This is the input for swing phase detection in the next session.

Test with a real golf swing video (DTL camera angle, 2-3 seconds). Print out landmark data for a few frames to verify it looks reasonable. Save a debug image with the skeleton drawn on one frame using MediaPipe's drawing utils. Write a unit test with a known test image that verifies landmarks are detected and returned in the correct format.
```

---

## SESSION 7: Swing Phase Detection (You)

```
Create backend/app/services/swing_detector.py. Implement the swing phase detection algorithm from CLAUDE.md. Input: list of frames with their landmarks. Output: dict mapping each of the 8 swing phases to a frame_number.

The algorithm:
1. Extract lead wrist Y-position across all frames (landmark 15 for right-handed, 16 for left-handed — use player's dominant_hand from DB)
2. Smooth with moving average (window=5)
3. Compute velocity (first derivative)
4. Detect: ADDRESS = first stable low-velocity period. TOP = global max of wrist Y. IMPACT = global min of wrist Y after TOP. TAKEAWAY, MID_BACKSWING, MID_DOWNSWING, MID_FOLLOW_THROUGH, FINISH = derived as described in CLAUDE.md.

Test with 3 different swing videos. Print detected phases with frame numbers. Visually verify by saving the detected phase frames as debug images.

Write unit tests: create a synthetic wrist-Y trajectory (e.g., a parabolic curve) where you know the answer — verify TOP is detected at the peak, IMPACT at the trough, etc. Write a test for left-handed detection (landmark 16 instead of 15).
```

---

## SESSION 8: Angle Calculation (Developer)

```
Create backend/app/services/angle_calculator.py. Implement the calc_angle function from CLAUDE.md and compute all golf-specific joint angles for a given frame's landmarks. The angles to compute for each frame: spine_angle, knee_flex_lead, knee_flex_trail, hip_hinge, lead_elbow, trail_elbow, shoulder_rotation (from shoulder line vs camera), hip_rotation (from hip line vs camera). Handle both right-handed and left-handed players by swapping lead/trail sides. Return a dict: {angle_name: value_in_degrees}.

Write unit tests with hardcoded landmark positions where you can hand-calculate the expected angle. Test: a 90° angle returns 90, a 180° angle returns 180, left-handed swaps lead/trail correctly. At least 5 test cases covering different angle types.
```

---

## SESSION 9: Frame Annotation — 3 View Modes (Developer)

```
Create backend/app/services/annotator.py. Implement generate_frame_views() as described in CLAUDE.md. It takes a raw frame (OpenCV image), keypoints, joint_angles, and optional deviations. It returns 3 images:

1. RAW: the unmodified frame
2. OVERLAY: raw frame + pose skeleton drawn on top + angle measurements as text + deviation markers color-coded (green/yellow/red per CLAUDE.md thresholds)
3. SKELETON: same skeleton and angles drawn on a dark background (#0a0f0d) with no photo

Use the ANNOTATION_STYLE config from CLAUDE.md for colors and sizes. Save all 3 to S3 under the paths defined in CLAUDE.md. Create frame records in DB with all 3 s3 keys populated.

Write tests: generate_frame_views returns exactly 3 images, overlay image has different pixel values than raw (skeleton was drawn), skeleton image background is dark. Test with a real frame from a test video.
```

---

## SESSION 10: Wire the Full Pipeline (Developer)

```
Wire together steps 4-8 in the process_video Celery task. After frame extraction: run pose estimation on all frames, detect swing phases, extract the 8 canonical frames, calculate joint angles for each, generate all 3 view modes (raw/overlay/skeleton) for each canonical frame, upload all images to S3, create frame records in DB. Set video status='analyzed' when done. Set status='error' with message if any step fails — clean up partial artifacts on failure (delete temp files, any partial S3 uploads). Log each step transition with structlog.

Write an integration test (@pytest.mark.slow): upload a test video, trigger the full pipeline, verify status becomes 'analyzed', verify 8 frame records created with all 3 S3 keys populated, verify joint angles exist. Also test that a bad video results in status='error' with a message.
```

---

## SESSION 11: Frames API (Developer)

```
Build the frames endpoints. GET /api/v1/videos/:id/frames returns all frames for a video, each with: id, swing_phase, frame_number, images (raw, overlay, skeleton presigned URLs), joint_angles, is_reference. GET /api/v1/frames/:id returns a single frame with full detail. PUT /api/v1/frames/:id/reference (coach only) marks/unmarks a frame as a reference frame for this player+phase. GET /api/v1/players/:id/references returns all reference frames for a player grouped by swing phase.

Write tests: get frames returns all 8 phases, single frame returns correct S3 URLs, mark/unmark reference, only coach can set reference (403 for player), player references grouped correctly.
```

---

## SESSION 12: Comparison Engine (You)

```
Create backend/app/services/comparator.py. When a new video is processed and the player has reference frames, compare each canonical frame against the player's reference for the same phase. For each angle, compute: {current, reference, delta, severity} where severity is "ok" (<5°), "minor" (5-15°), or "major" (>15°). Compute an overall_score (0-100) using the ANGLE_WEIGHTS from CLAUDE.md — higher weight angles affect the score more. Create comparison records in DB. Integrate this into the process_video pipeline: after frame creation, if references exist, run comparison.

Write unit tests: known angle pairs produce expected severity, score calculation with known weights produces expected score (hand-calculate one example), comparison skipped gracefully when no reference exists. Test with a player who has reference frames set.
```

---

## SESSION 13: AI Feedback Integration (You)

```
Create backend/app/services/ai_feedback.py. Load prompt templates from the prompts/ directory. For each frame that has a comparison, send the overlay image (current) + reference overlay image to Claude Sonnet Vision API. Include the joint angles, deviations, player skill_level, dominant_hand, and club_type in the prompt. Parse Claude's response and save as ai_feedback_text in the comparison record. Use the swing_analysis.txt prompt for individual frames. If no reference exists, still send the frame with the prompt but skip the comparison section. Integrate into the process_video pipeline as step 9.

Write tests: mock the Claude API call (use unittest.mock.patch on the anthropic client), verify prompt includes correct angles and deviations, verify ai_feedback_text is saved to DB. Test with and without reference frames.
```

---

## SESSION 14: Coach Dashboard — Login & Layout (Developer)

```
Build the coach login page at /login using shadcn Card, Input, Button and React Hook Form + Zod for validation. On success, store the JWT in the auth Zustand store. Set up protected routes — redirect to /login if not authenticated. Build the main layout with a sidebar (shadcn ScrollArea) showing the review queue and a main content area. The sidebar lists pending reviews from GET /api/v1/coach/queue — each item shows player avatar (initials), name, handicap, club, score badge, time ago, and flagged issue. Use TanStack Query to fetch the queue.

Write tests: login form validates email/password required, successful login stores token in Zustand, protected route redirects when unauthenticated.
```

---

## SESSION 15: Coach Dashboard — Swing Review Page (Developer)

```
Build the swing review page — the main content area when a queue item is selected. Show: player header (name, handicap, club, time), the view mode toggle bar (Photo/Overlay/Skeleton with Angles and Ghost checkboxes from CLAUDE.md), phase selector strip with status dots, and side-by-side FrameViewer components that display the frame images from the API based on selected view mode. Below the frames: AI suggestion card and coach note textarea (React Hook Form). Add an "Approve & Send" button that POSTs coach feedback via the API. Use TanStack Query mutations with optimistic updates so it feels instant. All 3 view modes must be wired to the correct S3 URLs from the frames API.

Write tests: view mode toggle switches displayed image URL, phase selector changes displayed frames, feedback form validates note is required.
```

---

## SESSION 16: Coach Dashboard — Player List (Developer)

```
Build the player list page at /players. Show a grid of player cards (shadcn Card) with: name, avatar, handicap, assigned coach, swing count, average score, trend arrow. Clicking a card goes to /players/:id. Use TanStack Query for data fetching with search filtering.

Write tests: player cards render from API data, search filters the list, clicking card navigates to detail page.
```

---

## SESSION 17: Coach Dashboard — Player Detail (Developer)

```
Build the player detail page at /players/:id. Show: player profile header, reference frames gallery (grouped by phase — coach can click to view/set references), video history list (most recent first, each showing score, phases, AI summary), and a simple progress chart showing average score over time (use recharts).

Write tests: profile data renders, video history sorted most recent first, reference frame toggle calls the API.
```

---

## SESSION 18: Player App — Home Screen (Developer)

```
Build the player app home screen (Swings tab). Show: weekly stats strip (avg score, vs last week, coach reviews), and a scrollable list of uploaded swings. Each swing card shows: score badge, club type, date, phase health bar (8 colored segments), AI summary text, and coach note if reviewed. Tapping a card navigates to the swing detail screen. Use TanStack Query to fetch from GET /api/v1/players/:id/videos.

No automated tests for this session (React Native testing setup is lower priority). Manual QA: verify list loads, cards display correct data, navigation works.
```

---

## SESSION 19: Player App — Swing Detail (Developer)

```
Build the swing detail screen. Show: header with club and score, side-by-side frame viewer (current vs reference) with the Photo/Analysis toggle at the bottom (2 modes only for players as per CLAUDE.md), phase selector strip, angle breakdown table, AI coach feedback card, and coach feedback card if available. All data comes from GET /api/v1/videos/:id which includes frames and feedback.

Manual QA: verify Photo/Analysis toggle switches images, phase selector works, all data displays correctly.
```

---

## SESSION 20: Player App — Video Capture (Developer)

```
Build the video capture screen. Use expo-camera to show the camera preview. Overlay a guide rectangle showing the player where to position themselves (60-70% of frame height). Show text prompts: "Position camera at belt height" and "Stand 8-10 feet from camera". Add a record button that captures video. Limit recording to 8 seconds max (auto-stop). Allow selecting camera_angle (DTL or Face-On) and club_type before recording.

Manual QA: test on a real device (camera doesn't work in simulators). Verify guide overlay displays, recording stops at 8s, camera_angle and club_type selection works.
```

---

## SESSION 21: Player App — Upload Flow (Developer)

```
Build the upload flow. After recording, show a preview of the video. User confirms or re-records. On confirm: upload to POST /api/v1/videos/upload with the video file, camera_angle, and club_type. Show upload progress bar. After upload completes, poll GET /api/v1/videos/:id/status every 3 seconds. Show processing animation. When status becomes 'analyzed', navigate to the swing detail screen with the results. Handle errors gracefully — show the error message from the API with a retry option.

Manual QA: test full upload → process → results flow end-to-end on a real device.
```

---

## SESSION 22: Feedback System (Developer)

```
Build the feedback endpoints. POST /api/v1/videos/:id/feedback accepts {feedback_type, summary, drill_recommendations, priority_fixes} from coaches. GET /api/v1/videos/:id/feedback returns all feedback for a video. GET /api/v1/players/:id/feedback returns paginated feedback history. Build PUT /api/v1/feedback/:id for editing. When coach submits feedback, set video status='reviewed'. Send a push notification to the player via Firebase (or just log it for now and add Firebase later).

Write tests: create feedback, get feedback for video, get feedback history paginated, update feedback, status transitions to 'reviewed', only coach can create feedback (403 for player).
```

---

## SESSION 23: Player Progress (Developer)

```
Build GET /api/v1/players/:id/progress. Return: angles_over_time (rolling averages of key angles per week), consistency_scores by phase, total swings per week, and overall score trend. Create a Celery periodic task that runs nightly to compute and store progress_snapshots. Build the Progress tab in the player app — show a line chart (recharts or Victory Native) of overall score over time, and a breakdown of which phases are improving vs which need work. Keep it simple and motivating.

Write tests for the progress API: verify returned data structure, verify snapshot computation with known input data, verify empty state (new player with no videos).
```

---

## SESSION 24: Baseline Comparison Feedback (You)

```
Build the baseline comparison AI feedback. When a player has reference frames and a comparison exists, use the baseline_comparison.txt prompt to generate a comparison-specific feedback message. This is different from the per-frame swing_analysis feedback — it specifically addresses what changed vs their personal best. Also build the progress summary — when a coach requests or on a weekly schedule, use the progress_summary.txt prompt to generate a written progress report for each player. Store in feedback table with type='ai_progress'.

Write tests: mock Claude API, verify baseline_comparison prompt includes reference angles, verify progress_summary prompt includes trend data, verify feedback stored with correct type.
```

---

## SESSION 25: Reference Ghost Overlay (Developer)

```
Build the reference ghost overlay feature in the coach dashboard. When the coach is in Overlay view mode and toggles the Ghost checkbox, fetch the reference frame's keypoints from the API. Render the reference skeleton as a faded yellow dashed SVG overlay on top of the current frame's overlay image. Use an SVG layer positioned absolutely over the frame image. The ghost skeleton should use the reference frame's keypoints_json to draw lines between landmarks. This is client-side rendering — not a separate S3 image.

Write tests: Ghost checkbox only enabled in Overlay mode, SVG overlay renders when Ghost is on, SVG uses reference frame keypoints.
```

---

## SESSION 26: Coach Dashboard — Loading & Error States (Developer)

```
Add loading states throughout the coach dashboard using shadcn Skeleton components. Add error states with retry buttons. Add toast notifications (shadcn Toast) for: feedback submitted, video processing complete, errors. Add keyboard shortcuts: arrow keys to navigate between queue items, Enter to approve and send, Escape to clear the note field.

No new tests needed — this is UI polish. Manual QA: verify skeletons appear during loading, errors show retry, toasts appear on actions, keyboard shortcuts work.
```

---

## SESSION 27: Coach Dashboard — Stats Overview (Developer)

```
Build the coach stats overview at /dashboard. Show: cards with total players, pending reviews, reviews completed this week, average response time. Below that, a list of players sorted by "needs attention" (most recent unreviewed swings first). Add a simple notification badge on the sidebar showing the count of pending reviews.

Write tests: stats cards render from API data, "needs attention" list sorted correctly.
```

---

## SESSION 28: Player App — Polish (Developer)

```
Add loading skeletons throughout the player app for all data-fetching screens. Add pull-to-refresh on the swings list. Add empty states — "No swings yet, record your first!" with a CTA button. Handle offline state gracefully — show cached data if available, show "You're offline" banner if not. Add haptic feedback on the record button.

No new tests — UI polish. Manual QA on device.
```

---

## SESSION 29: Player App — Push Notifications (Developer)

```
Build push notifications. Integrate Firebase Cloud Messaging in the player app. Register device token on login, send to backend. When video processing completes or coach sends feedback, trigger a push notification. Tapping the notification navigates to the relevant swing detail screen.

Write backend tests: device token registration endpoint, notification trigger on video complete, notification trigger on feedback submitted (mock Firebase).
```

---

## SESSION 30: Admin Role & Pages (Developer)

```
Build the admin role. Add a role field to coaches (coach, admin). Admins can: see all players across all coaches, add/remove coaches (POST/DELETE /api/v1/admin/coaches), add players (POST /api/v1/admin/players), view academy-wide stats. Build a simple admin page in the coach dashboard at /admin — only visible to admin role. Show player and coach management tables with shadcn DataTable.

Write tests: admin can list all players, non-admin gets 403 on admin endpoints, add/remove coach, add player.
```

---

## SESSION 31: Auth Hardening (Developer)

```
Harden auth throughout the app. Add rate limiting on OTP endpoints (max 5 attempts per phone per 15 minutes). Add token refresh flow — when JWT is about to expire, silently refresh. Add logout that clears tokens. Add "forgot password" flow for coaches (send reset link to email — for now just log the link). Review all endpoints for proper role-based access control.

Write tests: OTP rate limiting (6th attempt blocked), token refresh returns new token, expired token triggers refresh, all role-based access reviewed (create a test matrix).
```

---

## SESSION 32: Docker & Deployment Prep (Developer)

```
Write a Dockerfile for the backend (Python 3.11-slim, install deps, run uvicorn). Write a Dockerfile for the coach dashboard (Node build, serve with nginx). Update docker-compose.yml with: backend, celery worker, coach-dashboard, PostgreSQL, Redis, MinIO. Add a production docker-compose.prod.yml that uses real S3 instead of MinIO and sets production environment variables. Test that docker-compose -f docker-compose.prod.yml up builds and runs everything.

No new tests — verify existing tests pass inside Docker: docker-compose exec backend pytest.
```

---

## SESSION 33: Integration Tests & Coverage Gaps (Developer)

```
This session is NOT for writing all tests from scratch — tests should already exist from previous sessions. This session is for:

1. Full end-to-end integration test: upload a video → pipeline processes → coach reviews → player sees feedback. Test the entire happy path as a single flow.
2. Run coverage report (pytest --cov=app --cov-report=term-missing). Identify gaps in backend/app/services/ and backend/app/api/ — write tests for any service function or endpoint below 70% coverage.
3. Edge case tests: concurrent uploads, very short videos (1s), very long club names, Unicode player names, player with no reference frames yet.
4. Test error recovery: S3 down during upload (StorageError handled), Claude API timeout (feedback saved as null, not crash), Redis down during OTP (graceful failure).

Target: 80%+ coverage on services/, 70%+ on api/.
```

---

## SESSION 34: Deploy to Production (You)

```
Deploy to a VPS (DigitalOcean or AWS Lightsail). Set up: domain (swinglens.com or swinglens.in), SSL via Let's Encrypt, nginx reverse proxy to backend and coach dashboard, S3 bucket in ap-south-1, environment variables in production. Test the full flow: coach logs in, player uploads a video, video gets processed, coach reviews frames in all 3 view modes, sends feedback, player sees it on their phone.

Run the full test suite on the production build before going live. Verify all environment variables are set. Verify S3 permissions. Verify Celery worker is processing tasks.
```

---

## Summary of Changes

| What                | Before                     | After                                                                                                                         |
| ------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Linting/Formatting  | Not set up                 | ESLint + Prettier in 1c/1d, Ruff in backend (already in CLAUDE.md), pre-commit hooks in repo root                             |
| Testing per session | None until Session 33      | Every session with services/APIs includes "Write tests" with specific test cases listed                                       |
| Error handling      | Mentioned but not enforced | Custom exceptions from Session 2 onward, pipeline error recovery pattern, frontend error handling via TanStack Query + toasts |
| Logging             | structlog mentioned        | Enforced from Session 5 onward with video_id + step_name context                                                              |
| Session 33          | "Write all tests"          | Integration tests + coverage gap filling only (tests already written)                                                         |
| Player app testing  | Full automated tests       | Manual QA only (React Native testing setup not worth the overhead for MVP)                                                    |
