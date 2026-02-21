'use client';

import React, { useState } from 'react';
import { BlogOutput, LinkedInOutput, TwitterOutput, CritiqueTrace, BlogScores, ShortFormScores } from '@/lib/types';

interface Props {
    blog: BlogOutput;
    linkedin: LinkedInOutput;
    twitter: TwitterOutput;
    critiqueTrace: CritiqueTrace;
}

type Asset = 'blog' | 'linkedin' | 'twitter';

function DeltaBadge({ delta }: { delta: number | null }) {
    if (delta === null) return null;
    const positive = delta > 0;
    const zero = delta === 0;
    return (
        <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded-full ${zero ? 'text-gray-500 bg-gray-800'
                : positive ? 'text-emerald-400 bg-emerald-500/15 border border-emerald-500/25'
                    : 'text-red-400 bg-red-500/15 border border-red-500/25'
            }`}>
            {positive ? '+' : ''}{delta?.toFixed(2)}
        </span>
    );
}

function BlogScoreRow({ label, score, prev }: { label: string; score: number; prev?: number }) {
    const delta = prev !== undefined ? score - prev : null;
    const color = score >= 7 ? 'text-emerald-400' : score >= 5 ? 'text-amber-400' : 'text-red-400';
    return (
        <div className="flex items-center justify-between text-xs py-1">
            <span className="text-gray-500">{label}</span>
            <div className="flex items-center gap-2">
                {delta !== null && <DeltaBadge delta={delta} />}
                <span className={`font-mono font-bold ${color}`}>{score.toFixed(1)}</span>
            </div>
        </div>
    );
}

function BlogScoresCard({ scores, prev, draftNum }: { scores: BlogScores; prev?: BlogScores; draftNum: number }) {
    return (
        <div className="rounded-xl bg-gray-900/60 border border-gray-700/50 p-4">
            <p className="text-xs text-indigo-400 font-medium mb-3">Draft {draftNum}</p>
            <BlogScoreRow label="Hook Strength" score={scores.hook_strength} prev={prev?.hook_strength} />
            <BlogScoreRow label="Clarity" score={scores.clarity} prev={prev?.clarity} />
            <BlogScoreRow label="Authority Tone" score={scores.authority_tone} prev={prev?.authority_tone} />
            <BlogScoreRow label="Differentiation" score={scores.differentiation} prev={prev?.differentiation} />
            <BlogScoreRow label="Logical Structure" score={scores.logical_structure} prev={prev?.logical_structure} />
            <BlogScoreRow label="Brand Fit" score={scores.datavex_brand_fit} prev={prev?.datavex_brand_fit} />
        </div>
    );
}

function SFScoresCard({ scores, prev, draftNum }: { scores: ShortFormScores; prev?: ShortFormScores; draftNum: number }) {
    const delta = (s: ShortFormScores) =>
        (s.hook_density + s.platform_native_feel + s.engagement_trigger_strength + s.shareability + s.brand_fit) / 5;

    return (
        <div className="rounded-xl bg-gray-900/60 border border-gray-700/50 p-4">
            <div className="flex items-center justify-between mb-3">
                <p className="text-xs text-indigo-400 font-medium">Draft {draftNum}</p>
                {prev && <DeltaBadge delta={Math.round((delta(scores) - delta(prev)) * 100) / 100} />}
            </div>
            {[
                ['Hook Density', scores.hook_density, prev?.hook_density],
                ['Platform Feel', scores.platform_native_feel, prev?.platform_native_feel],
                ['Engagement', scores.engagement_trigger_strength, prev?.engagement_trigger_strength],
                ['Shareability', scores.shareability, prev?.shareability],
                ['Brand Fit', scores.brand_fit, prev?.brand_fit],
            ].map(([label, val, pval]) => (
                <div key={label as string} className="flex items-center justify-between text-xs py-1">
                    <span className="text-gray-500">{label as string}</span>
                    <div className="flex items-center gap-2">
                        {pval !== undefined && <DeltaBadge delta={Math.round(((val as number) - (pval as number)) * 100) / 100} />}
                        <span className={`font-mono font-bold ${(val as number) >= 7 ? 'text-emerald-400' : 'text-amber-400'}`}>
                            {(val as number).toFixed(1)}
                        </span>
                    </div>
                </div>
            ))}
        </div>
    );
}

export default function CritiqueTracePanel({ blog, linkedin, twitter, critiqueTrace }: Props) {
    const [asset, setAsset] = useState<Asset>('blog');

    return (
        <section className="panel space-y-5">
            <p className="panel-title">Critique Trace</p>

            {/* Asset Tabs */}
            <div className="flex border-b border-gray-800 -mx-1">
                {(['blog', 'linkedin', 'twitter'] as Asset[]).map(a => (
                    <button
                        key={a}
                        onClick={() => setAsset(a)}
                        className={`px-4 py-2 text-sm font-medium capitalize transition-colors mx-1 ${asset === a
                                ? 'text-indigo-400 border-b-2 border-indigo-500'
                                : 'text-gray-500 hover:text-gray-300'
                            }`}
                    >
                        {a === 'twitter' ? 'Twitter' : a[0].toUpperCase() + a.slice(1)}
                    </button>
                ))}
            </div>

            {asset === 'blog' && (
                <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {critiqueTrace.blog_scores_by_draft.map((scores, i) => (
                            <BlogScoresCard
                                key={i}
                                scores={scores}
                                prev={i > 0 ? critiqueTrace.blog_scores_by_draft[i - 1] : undefined}
                                draftNum={i + 1}
                            />
                        ))}
                    </div>
                    <div className="space-y-3">
                        {blog.evolution_log.map((entry, i) => (
                            <div key={i} className="rounded-xl bg-gray-900/40 border border-gray-800 p-4">
                                <div className="flex items-center gap-3 mb-2">
                                    <span className="text-xs text-indigo-400 font-medium">Draft {entry.draft_number}</span>
                                    {entry.score_delta !== null && <DeltaBadge delta={entry.score_delta} />}
                                </div>
                                <p className="text-xs text-gray-500 italic">{entry.key_changes_made}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {asset === 'linkedin' && (
                <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {critiqueTrace.linkedin_scores_by_draft.map((scores, i) => (
                            <SFScoresCard
                                key={i}
                                scores={scores}
                                prev={i > 0 ? critiqueTrace.linkedin_scores_by_draft[i - 1] : undefined}
                                draftNum={i + 1}
                            />
                        ))}
                    </div>
                    <div className="space-y-2">
                        {linkedin.evolution_log.map((entry, i) => (
                            <div key={i} className="rounded-xl bg-gray-900/40 border border-gray-800 p-3">
                                <div className="flex items-center gap-3 mb-1">
                                    <span className="text-xs text-indigo-400 font-medium">Draft {entry.draft_number}</span>
                                    {entry.score_delta !== null && <DeltaBadge delta={entry.score_delta} />}
                                </div>
                                <p className="text-xs text-gray-500 italic">{entry.key_changes_made}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {asset === 'twitter' && (
                <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {critiqueTrace.twitter_scores_by_draft.map((scores, i) => (
                            <SFScoresCard
                                key={i}
                                scores={scores}
                                prev={i > 0 ? critiqueTrace.twitter_scores_by_draft[i - 1] : undefined}
                                draftNum={i + 1}
                            />
                        ))}
                    </div>
                    <div className="space-y-2">
                        {twitter.evolution_log.map((entry, i) => (
                            <div key={i} className="rounded-xl bg-gray-900/40 border border-gray-800 p-3">
                                <div className="flex items-center gap-3 mb-1">
                                    <span className="text-xs text-indigo-400 font-medium">Draft {entry.draft_number}</span>
                                    {entry.score_delta !== null && <DeltaBadge delta={entry.score_delta} />}
                                </div>
                                <p className="text-xs text-gray-500 italic">{entry.key_changes_made}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </section>
    );
}
