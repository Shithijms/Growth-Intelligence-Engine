"use client";

import { useState } from "react";

interface KeywordFormProps {
  onRun: (keyword: string) => void;
  loading: boolean;
}

export default function KeywordForm({ onRun, loading }: KeywordFormProps) {
  const [keyword, setKeyword] = useState("");

  return (
    <div className="flex flex-col gap-3 max-w-xl">
      <label htmlFor="keyword" className="text-sm font-medium text-[var(--muted)]">
        Keyword
      </label>
      <div className="flex gap-2">
        <input
          id="keyword"
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="e.g. RAG"
          className="flex-1 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-2.5 text-[var(--text)] placeholder:text-[var(--muted)] focus:border-[var(--accent)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)]"
          disabled={loading}
        />
        <button
          type="button"
          onClick={() => onRun(keyword)}
          disabled={loading || !keyword.trim()}
          className="rounded-lg bg-[var(--accent)] px-5 py-2.5 font-medium text-white hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Running…" : "Run pipeline"}
        </button>
      </div>
    </div>
  );
}
