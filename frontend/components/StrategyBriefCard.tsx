"use client";

import type { StrategyBrief as StrategyBriefType } from "@/services/api";

export default function StrategyBriefCard({ brief }: { brief: StrategyBriefType }) {
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
      <h2 className="text-lg font-semibold mb-3">Strategy brief</h2>
      <div className="space-y-4 text-sm">
        <div>
          <h3 className="font-medium text-[var(--muted)] mb-1">Signal summary</h3>
          <p className="text-[var(--text)]">{brief.signal_summary}</p>
        </div>
        <div>
          <h3 className="font-medium text-[var(--muted)] mb-1">Chosen angle</h3>
          <p className="text-[var(--text)] font-medium">{brief.chosen_angle}</p>
        </div>
        <div>
          <h3 className="font-medium text-[var(--muted)] mb-1">Why this angle wins</h3>
          <p className="text-[var(--text)]">{brief.why_this_angle_wins}</p>
        </div>
        {brief.rejected_angles.length > 0 && (
          <div>
            <h3 className="font-medium text-[var(--muted)] mb-1">Rejected angles</h3>
            <ul className="list-disc pl-5 space-y-1 text-[var(--text)]">
              {brief.rejected_angles.map((r, i) => (
                <li key={i}>
                  <span className="font-medium">{r.angle}</span>
                  <span className="text-[var(--muted)]"> — {r.reason_rejected}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        <div>
          <h3 className="font-medium text-[var(--muted)] mb-1">Platform strategy</h3>
          <p className="text-[var(--text)]">{brief.platform_strategy}</p>
        </div>
        <div>
          <h3 className="font-medium text-[var(--muted)] mb-1">Core thesis</h3>
          <p className="text-[var(--text)]">{brief.core_thesis}</p>
        </div>
      </div>
    </section>
  );
}
