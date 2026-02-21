"use client";

import { useState } from "react";
import KeywordForm from "@/components/KeywordForm";
import SignalCard from "@/components/SignalCard";
import StrategyBriefCard from "@/components/StrategyBriefCard";
import ContentTabs from "@/components/ContentTabs";
import CritiqueEvolution from "@/components/CritiqueEvolution";
import { runPipeline, type RunResponse, type PipelineResult } from "@/services/api";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<RunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleRun(keyword: string) {
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      const res = await runPipeline(keyword);
      setResponse(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  const result: PipelineResult | null = response?.result ?? null;

  return (
    <main className="min-h-screen p-6 md:p-10 max-w-5xl mx-auto">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-[var(--text)]">
          DataVex Growth Intelligence Engine
        </h1>
        <p className="text-[var(--muted)] mt-1">
          Keyword → Signal → Strategy → Content → Critique. One pipeline.
        </p>
      </header>

      <KeywordForm onRun={handleRun} loading={loading} />

      {error && (
        <div className="mt-4 rounded-lg border border-red-500/50 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {response && result && (
        <div className="mt-8 space-y-6">
          {/* Latency & abort */}
          <div className="flex flex-wrap gap-4 items-center text-sm">
            <span className="text-[var(--muted)]">
              Total latency: <strong className="text-[var(--text)]">{response.total_latency_seconds}s</strong>
            </span>
            {response.aborted && response.abort_reason && (
              <span className="text-amber-400">Aborted: {response.abort_reason}</span>
            )}
            {Object.keys(response.stage_timings_seconds).length > 0 && (
              <span className="text-[var(--muted)]">
                Stages:{" "}
                {Object.entries(response.stage_timings_seconds)
                  .map(([k, v]) => `${k}: ${v}s`)
                  .join(", ")}
              </span>
            )}
          </div>

          {result.signal_result && (
            <SignalCard signalResult={result.signal_result} />
          )}

          {result.strategy_brief && (
            <StrategyBriefCard brief={result.strategy_brief} />
          )}

          {result.content_assets && (
            <>
              <ContentTabs assets={result.content_assets} />
              <div className="grid gap-4 md:grid-cols-3">
                <CritiqueEvolution label="Blog" trace={result.content_assets.blog} />
                <CritiqueEvolution label="LinkedIn" trace={result.content_assets.linkedin} />
                <CritiqueEvolution label="Twitter/X" trace={result.content_assets.twitter_thread} />
              </div>
            </>
          )}
        </div>
      )}
    </main>
  );
}
