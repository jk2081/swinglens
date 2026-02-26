export interface ApiResponse<T> {
  data: T;
}

export interface ApiError {
  error: {
    message: string;
    code: string;
  };
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
  };
}

export interface Player {
  id: string;
  academy_id: string;
  coach_id: string;
  name: string;
  phone: string;
  handicap: number | null;
  skill_level: 'beginner' | 'intermediate' | 'advanced' | 'pro';
  dominant_hand: 'right' | 'left';
  created_at: string;
}

export interface Video {
  id: string;
  player_id: string;
  s3_key: string;
  camera_angle: 'dtl' | 'face_on' | null;
  club_type: string | null;
  status: 'uploading' | 'processing' | 'analyzed' | 'reviewed' | 'error';
  duration_ms: number | null;
  fps: number | null;
  error_message: string | null;
  uploaded_at: string;
  processed_at: string | null;
}

export interface FrameImages {
  raw: string;
  overlay: string;
}

export interface Frame {
  id: string;
  video_id: string;
  swing_phase: string;
  frame_number: number;
  images: FrameImages;
  joint_angles: Record<string, number>;
  is_reference: boolean;
}

export interface Feedback {
  id: string;
  video_id: string;
  player_id: string;
  coach_id: string | null;
  feedback_type: 'ai_instant' | 'coach_review';
  summary: string | null;
  drill_recommendations: { name: string; description: string; video_url: string }[];
  priority_fixes: { issue: string; phase: string; severity: string; description: string }[];
  is_read: boolean;
  created_at: string;
}
