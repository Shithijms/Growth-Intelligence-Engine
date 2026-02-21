"use client";

import { useState } from "react";
import type { ContentAssets } from "@/services/api";

export default function ContentTabs({ assets }: { assets: ContentAssets }) {
  const [tab, setTab] = useState<"blog" | "linkedin" | "twitter">("blog");
  const current = assets[tab === "twitter" ? "twitter_thread" : tab];

  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] overflow-hidden">
      <div className="flex border-b border-[var(--border)]">
        {(["blog", "linkedin", "twitter"] as const).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`px-5 py-3 text-sm font-medium capitalize ${
              tab === t
                ? "border-b-2 border-[var(--accent)] text-[var(--accent)]"
                : "text-[var(--muted)] hover:text-[var(--text)]"
            }`}
          >
            {t === "twitter" ? "Twitter/X" : t}
          </button>
        ))}
      </div>
      <div className="p-5 max-h-[420px] overflow-y-auto">
        <pre className="whitespace-pre-wrap font-sans text-sm text-[var(--text)]">
          {current.final_content}
        </pre>
      </div>
    </section>
  );
}
