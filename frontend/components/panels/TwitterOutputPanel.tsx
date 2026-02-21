'use client';

import React, { useState } from 'react';
import { TwitterOutput, CritiqueTrace, ShortFormScores } from '@/lib/types';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';

interface Props {
    data: TwitterOutput;
    critiqueTrace: CritiqueTrace;
}

function SFScoreChart({ scores }: { scores: ShortFormScores[] }) {
    const data = scores.map((s, i) => ({
        name: `D${i + 1}`,
        Hook: s.hook_density,
        'Platform': s.platform_native_feel,
        Engagement: s.engagement_trigger_strength,
        Share: s.shareability,
        Brand: s.brand_fit,
    }));
    return (
        <ResponsiveContainer width="100%" height={150}>
            <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <YAxis domain={[0, 10]} tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid rgba(99,102,241,0.3)', borderRadius: 8 }} />
                <Legend wrapperStyle={{ fontSize: 10, color: '#9ca3af' }} />
                <Line type="monotone" dataKey="Hook" stroke="#818cf8" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Platform" stroke="#34d399" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Engagement" stroke="#c084fc" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Share" stroke="#fb923c" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Brand" stroke="#f472b6" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
        </ResponsiveContainer>
    );
}

export default function TwitterOutputPanel({ data, critiqueTrace }: Props) {
    const [copied, setCopied] = useState(false);

    const handleCopyAll = () => {
        navigator.clipboard.writeText(data.tweets.join('\n\n'));
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <section className="panel space-y-5">
            <div className="flex items-center justify-between">
                <p className="panel-title mb-0">Twitter / X Thread</p>
                <button onClick={handleCopyAll} className="copy-btn">
                    {copied ? '✓ Copied All' : '⎘ Copy Thread'}
                </button>
            </div>

            {/* Score Chart */}
            {critiqueTrace.twitter_scores_by_draft.length > 0 && (
                <div className="rounded-xl bg-gray-900/60 border border-gray-700/50 p-4">
                    <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Score Evolution</p>
                    <SFScoreChart scores={critiqueTrace.twitter_scores_by_draft} />
                </div>
            )}

            {/* Tweet Cards */}
            <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
                {data.tweets.map((tweet, i) => (
                    <div
                        key={i}
                        className="rounded-xl bg-gray-900/60 border border-gray-700/50 p-4 space-y-2"
                    >
                        <div className="flex items-start gap-3">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
                                DV
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="text-sm font-semibold text-white">DataVex</span>
                                    <span className="text-xs text-gray-600">@datavex</span>
                                    {i === 0 && (
                                        <span className="ml-auto text-xs tag">Hook</span>
                                    )}
                                </div>
                                <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">{tweet}</p>
                                <div className="flex items-center justify-between mt-2">
                                    <div className="flex gap-4 text-xs text-gray-600">
                                        <span>💬</span><span>🔁</span><span>❤</span><span>↑</span>
                                    </div>
                                    <span className={`text-xs font-mono ${tweet.length > 280 ? 'text-red-400' : 'text-gray-600'}`}>
                                        {tweet.length}/280
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </section>
    );
}
