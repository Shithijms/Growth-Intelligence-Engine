'use client';

import React, { useState } from 'react';
import { StrategyBrief } from '@/lib/types';

interface Props {
    data: StrategyBrief;
}

export default function StrategyBriefPanel({ data }: Props) {
    const [openRejected, setOpenRejected] = useState<number | null>(null);

    return (
        <section className="panel space-y-5">
            <p className="panel-title">Strategy Brief</p>

            {/* Chosen Angle */}
            <div className="rounded-xl bg-gradient-to-br from-indigo-600/10 to-purple-600/10 border border-indigo-500/20 p-4">
                <p className="text-xs text-indigo-400 uppercase tracking-wider mb-1">Chosen Angle</p>
                <h3 className="text-base font-bold text-white leading-snug">{data.chosen_angle}</h3>
                <p className="text-xs text-gray-400 mt-2 leading-relaxed">{data.angle_rationale}</p>
            </div>

            {/* Core Thesis */}
            <div className="space-y-1">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Core Positioning Thesis</p>
                <p className="text-sm text-white/90 leading-relaxed italic">&ldquo;{data.core_positioning_thesis}&rdquo;</p>
            </div>

            {/* Competitive Gap */}
            <div className="space-y-1">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Competitive Gap Exploited</p>
                <p className="text-xs text-emerald-300/80">{data.competitive_gap_exploited}</p>
            </div>

            {/* Target Audience */}
            <div className="flex items-center gap-3">
                <span className="text-xs font-medium text-gray-500">Audience:</span>
                <span className="tag">{data.target_audience}</span>
            </div>

            {/* Authority Score */}
            <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-gray-900/60 border border-gray-700/50">
                <span className="text-xs text-gray-400">Estimated Authority Score</span>
                <div className="flex items-center gap-2">
                    <div className="w-24 score-bar-track">
                        <div
                            className="score-bar-fill bg-gradient-to-r from-indigo-500 to-purple-500"
                            style={{ width: `${data.estimated_authority_score}%` }}
                        />
                    </div>
                    <span className="text-sm font-bold text-indigo-400 font-mono">{data.estimated_authority_score}</span>
                </div>
            </div>

            {/* Platform Distribution */}
            <div className="space-y-2">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Platform Distribution</p>
                {(['blog', 'linkedin', 'twitter'] as const).map(platform => (
                    <div key={platform} className="flex gap-3 text-xs bg-gray-900/40 rounded-lg px-3 py-2">
                        <span className="text-indigo-400 capitalize font-medium shrink-0 w-14">{platform}</span>
                        <span className="text-gray-400">{data.platform_distribution_plan[platform]}</span>
                    </div>
                ))}
            </div>

            {/* Rejected Angles Accordion */}
            {data.rejected_angles.length > 0 && (
                <div className="space-y-2">
                    <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Rejected Angles ({data.rejected_angles.length})
                    </p>
                    {data.rejected_angles.map((ra, i) => (
                        <div
                            key={i}
                            className="rounded-lg border border-gray-800 overflow-hidden"
                        >
                            <button
                                onClick={() => setOpenRejected(openRejected === i ? null : i)}
                                className="w-full flex items-center justify-between px-4 py-2.5 text-left
                           hover:bg-gray-800/40 transition-colors"
                            >
                                <span className="text-sm text-gray-300 line-clamp-1">{ra.angle}</span>
                                <span className="text-gray-600 text-xs ml-2">{openRejected === i ? '▲' : '▼'}</span>
                            </button>
                            {openRejected === i && (
                                <div className="px-4 pb-3 text-xs text-gray-400 border-t border-gray-800 pt-2 leading-relaxed">
                                    {ra.reason}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </section>
    );
}
