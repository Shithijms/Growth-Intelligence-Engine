"use client";

import type { ContentWithCritiqueTrace } from "@/services/api";

function formatScores(s: { hook_strength: number; authority: number; differentiation: number; structure: number; platform_fit: number }) {
  const avg = (s.hook_strength + s.authority + s.differentiation + s.structure + s.platform_fit) / 5;
  return { ...s, average: avg.toFixed(1) };
}

export default function CritiqueEvolution({
  label,
  trace,
}: {
  label: string;
  trace: ContentWithCritiqueTrace;
}) {
  const { drafts, critiques, score_evolution } = trace;

  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
      <h3 className="text-base font-semibold mb-3">{label} — Critique evolution</h3>
      <div className="space-y-4">
        {drafts.map((draft, i) => (
          <div key={i} className="border-l-2 border-[var(--border)] pl-4">
            <p className="text-xs font-medium text-[var(--muted)] mb-1">Draft {i + 1}</p>
            {score_evolution[i] && (
              <p className="text-xs text-[var(--text)] mb-2">
                Scores: hook {score_evolution[i].hook_strength.toFixed(1)}, authority{" "}
                {score_evolution[i].authority.toFixed(1)}, differentiation{" "}
                {score_evolution[i].differentiation.toFixed(1)}, structure{" "}
                {score_evolution[i].structure.toFixed(1)}, platform{" "}
                {score_evolution[i].platform_fit.toFixed(1)} → avg{" "}
                {formatScores(score_evolution[i]).average}
              </p>
            )}
            {critiques[i] && (
              <p className="text-sm text-[var(--muted)] mb-2">Feedback: {critiques[i].feedback}</p>
            )}
            <pre className="whitespace-pre-wrap text-xs text-[var(--text)]/80 max-h-32 overflow-y-auto">
              {draft.slice(0, 500)}
              {draft.length > 500 ? "…" : ""}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}
