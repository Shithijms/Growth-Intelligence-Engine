"use client";

import type { SignalResult as SignalResultType } from "@/services/api";

export default function SignalCard({ signalResult }: { signalResult: SignalResultType }) {
  const { signal, confidence_score, confidence_breakdown, from_cache } = signalResult;
  const pct = Math.round(confidence_score * 100);

  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
      <h2 className="text-lg font-semibold mb-3">External signal</h2>
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <span className="inline-flex items-center rounded-full bg-[var(--accent)]/20 px-2.5 py-0.5 text-sm text-[var(--accent)]">
          Confidence: {pct}%
        </span>
        {from_cache && (
          <span className="rounded-full bg-[var(--muted)]/30 px-2.5 py-0.5 text-sm text-[var(--muted)]">
            From cache
          </span>
        )}
      </div>
      <h3 className="font-medium text-[var(--text)]">{signal.title}</h3>
      <p className="text-sm text-[var(--muted)] mt-0.5">
        {signal.source} · {signal.source_type}
      </p>
      <p className="mt-2 text-sm text-[var(--text)]/90">{signal.summary}</p>
      {Object.keys(confidence_breakdown).length > 0 && (
        <div className="mt-3 text-xs text-[var(--muted)]">
          Breakdown:{" "}
          {Object.entries(confidence_breakdown)
            .map(([k, v]) => `${k}: ${typeof v === "number" ? (v * 100).toFixed(0) : v}%`)
            .join(", ")}
        </div>
      )}
    </section>
  );
}
