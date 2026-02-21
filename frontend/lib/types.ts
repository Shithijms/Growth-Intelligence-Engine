// TypeScript types mirroring backend Pydantic models

export interface CandidateSignal {
  title: string;
  url: string;
  date: string;
  summary: string;
  relevance_score: number;
}

export interface SignalConfidenceScores {
  authority: number;
  recency: number;
  relevance: number;
  novelty: number;
  composite: number;
}

export interface SignalReport {
  selected_signal: CandidateSignal;
  confidence_scores: SignalConfidenceScores;
  validated_facts: string[];
  competitor_angles: string[];
  identified_gaps: string[];
}

export interface RejectedAngle {
  angle: string;
  reason: string;
}

export interface PlatformDistributionPlan {
  blog: string;
  linkedin: string;
  twitter: string;
}

export interface StrategyBrief {
  signal_summary: string;
  chosen_angle: string;
  angle_rationale: string;
  rejected_angles: RejectedAngle[];
  competitive_gap_exploited: string;
  core_positioning_thesis: string;
  platform_distribution_plan: PlatformDistributionPlan;
  target_audience: string;
  estimated_authority_score: number;
}

export interface BlogScores {
  hook_strength: number;
  clarity: number;
  authority_tone: number;
  differentiation: number;
  logical_structure: number;
  datavex_brand_fit: number;
}

export interface BlogDraftEntry {
  draft_number: number;
  draft: string;
  scores: BlogScores;
  key_changes_made: string;
  score_delta: number | null;
}

export interface BlogOutput {
  final_draft: string;
  meta_title: string;
  meta_description: string;
  evolution_log: BlogDraftEntry[];
}

export interface ShortFormScores {
  hook_density: number;
  platform_native_feel: number;
  engagement_trigger_strength: number;
  shareability: number;
  brand_fit: number;
}

export interface ShortFormDraftEntry {
  draft_number: number;
  draft: string;
  scores: ShortFormScores;
  key_changes_made: string;
  score_delta: number | null;
}

export interface LinkedInOutput {
  final_draft: string;
  evolution_log: ShortFormDraftEntry[];
}

export interface TwitterOutput {
  tweets: string[];
  evolution_log: ShortFormDraftEntry[];
}

export interface CritiqueTrace {
  blog_scores_by_draft: BlogScores[];
  linkedin_scores_by_draft: ShortFormScores[];
  twitter_scores_by_draft: ShortFormScores[];
}

export interface GateDecision {
  asset: string;
  gate_passed: boolean;
  trigger_reason: string;
  final_scores: Record<string, number>;
}

export interface RunMetadata {
  keyword: string;
  timestamp: string;
  total_pipeline_duration_seconds: number;
}

export interface PipelineOutput {
  run_metadata: RunMetadata;
  signal_report: SignalReport;
  strategy_brief: StrategyBrief;
  blog: BlogOutput;
  linkedin: LinkedInOutput;
  twitter_thread: TwitterOutput;
  critique_trace: CritiqueTrace;
  quality_gate_log: GateDecision[];
}

export interface ProgressEvent {
  type: 'progress';
  stage: string;
  label: string;
  node: string;
}

export interface PipelineStage {
  id: string;
  label: string;
  completed: boolean;
  active: boolean;
}
