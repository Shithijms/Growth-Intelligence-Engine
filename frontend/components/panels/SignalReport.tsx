'use client';

import React from 'react';
import { SignalReport as SignalReportType } from '@/lib/types';

interface Props {
    data: SignalReportType;
}

function ScoreBar({ label, value }: { label: string; value: number }) {
    const pct = (value / 10) * 100;
    const color =
        value >= 8 ? 'from-emerald-500 to-teal-400' :
            value >= 6 ? 'from-indigo-500 to-purple-500' :
                'from-amber-500 to-orange-400';

    return (
        <div className="space-y-1">
            <div className="flex justify-between text-xs">
                <span className="text-gray-400">{label}</span>
                <span className={`font-mono font-bold ${value >= 7 ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {value.toFixed(1)}
                </span>
            </div>
            <div className="score-bar-track">
                <div className={`score-bar-fill bg-gradient-to-r ${color}`} style={{ width: `${pct}%` }} />
            </div>
        </div>
    );
}

export default function SignalReport({ data }: Props) {
    const { selected_signal, confidence_scores, validated_facts, competitor_angles, identified_gaps } = data;

    return (
        <section className="panel space-y-5">
            <p className="panel-title">Signal Intelligence Report</p>

            {/* Selected Signal Card */}
            <div className="rounded-xl bg-gray-900/60 border border-gray-700/50 p-4 space-y-2">
                <div className="flex items-start justify-between gap-3">
                    <h3 className="text-sm font-semibold text-white leading-snug">{selected_signal.title}</h3>
                    <span className="shrink-0 tag">{selected_signal.date}</span>
                </div>
                <a
                    href={selected_signal.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-indigo-400 hover:text-indigo-300 underline underline-offset-2 break-all"
                >
                    {selected_signal.url}
                </a>
                <p className="text-xs text-gray-400 leading-relaxed">{selected_signal.summary}</p>
            </div>

            {/* Confidence Scores */}
            <div className="space-y-2.5">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence Scores</p>
                <ScoreBar label="Source Authority" value={confidence_scores.authority} />
                <ScoreBar label="Recency" value={confidence_scores.recency} />
                <ScoreBar label="Keyword Relevance" value={confidence_scores.relevance} />
                <ScoreBar label="Novelty" value={confidence_scores.novelty} />
                <div className="pt-1 border-t border-gray-800">
                    <ScoreBar label="Composite Score" value={confidence_scores.composite} />
                </div>
            </div>

            {/* Validated Facts */}
            {validated_facts.length > 0 && (
                <div className="space-y-2">
                    <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Validated Facts</p>
                    <ul className="space-y-1.5">
                        {validated_facts.map((fact, i) => (
                            <li key={i} className="flex gap-2 text-xs text-gray-300">
                                <span className="text-indigo-400 shrink-0 mt-0.5">▸</span>
                                <span>{fact}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Competitor Angles */}
            {competitor_angles.length > 0 && (
                <div className="space-y-2">
                    <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Competitor Angles</p>
                    <div className="flex flex-wrap gap-1.5">
                        {competitor_angles.map((a, i) => (
                            <span key={i} className="px-2 py-1 text-xs rounded-lg bg-gray-800 text-gray-400">{a}</span>
                        ))}
                    </div>
                </div>
            )}

            {/* Identified Gaps */}
            {identified_gaps.length > 0 && (
                <div className="space-y-2">
                    <p className="text-xs font-medium text-emerald-500/80 uppercase tracking-wider">
                        ✦ Identified Gaps (Opportunities)
                    </p>
                    <ul className="space-y-1.5">
                        {identified_gaps.map((gap, i) => (
                            <li key={i} className="flex gap-2 text-xs text-emerald-300/80 bg-emerald-500/5 border border-emerald-500/15 rounded-lg px-3 py-2">
                                <span className="shrink-0">✦</span>
                                <span>{gap}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </section>
    );
}
