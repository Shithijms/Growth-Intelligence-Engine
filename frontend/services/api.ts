/**
 * API client for DataVex Growth Intelligence Engine backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface RunResponse {
  success: boolean;
  aborted: boolean;
  abort_reason: string | null;
  total_latency_seconds: number;
  stage_timings_seconds: Record<string, number>;
  result: PipelineResult | null;
}

export interface PipelineResult {
  keyword: string;
  signal_result: SignalResult | null;
  gap_analysis: GapAnalysis | null;
  strategy_brief: StrategyBrief | null;
  positioning: PositioningHooks | null;
  content_assets: ContentAssets | null;
  total_latency_seconds: number;
  aborted: boolean;
  abort_reason: string | null;
  stage_timings_seconds: Record<string, number>;
}

export interface ExternalSignal {
  title: string;
  source: string;
  source_type: string;
  summary: string;
  url?: string;
  citation_count?: number;
  year?: number;
  raw_snippet?: string;
}

export interface SignalResult {
  signal: ExternalSignal;
  confidence_score: number;
  confidence_breakdown: Record<string, number>;
  from_cache: boolean;
  abort_reason?: string | null;
}

export interface GapAnalysis {
  saturated_angles: string[];
  common_narratives: string[];
  angles_to_avoid: string[];
  summary: string;
}

export interface RejectedAngle {
  angle: string;
  reason_rejected: string;
}

export interface StrategyBrief {
  signal_summary: string;
  chosen_angle: string;
  why_this_angle_wins: string;
  rejected_angles: RejectedAngle[];
  platform_strategy: string;
  core_thesis: string;
}

export interface PositioningHooks {
  blog_tail_insight: string;
  linkedin_mention: string;
  twitter_mention: string;
  philosophy_tie: string;
}

export interface CritiqueScores {
  hook_strength: number;
  authority: number;
  differentiation: number;
  structure: number;
  platform_fit: number;
}

export interface CritiqueResult {
  scores: CritiqueScores;
  feedback: string;
  draft_number: number;
}

export interface ContentWithCritiqueTrace {
  final_content: string;
  drafts: string[];
  critiques: CritiqueResult[];
  score_evolution: CritiqueScores[];
}

export interface ContentAssets {
  blog: ContentWithCritiqueTrace;
  linkedin: ContentWithCritiqueTrace;
  twitter_thread: ContentWithCritiqueTrace;
}

export async function runPipeline(keyword: string): Promise<RunResponse> {
  const res = await fetch(`${API_BASE}/api/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ keyword: keyword.trim() }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }
  return res.json();
}
