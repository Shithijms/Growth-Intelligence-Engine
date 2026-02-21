'use client';

import React, { useState } from 'react';
import { LinkedInOutput, CritiqueTrace, ShortFormScores } from '@/lib/types';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';

interface Props {
    data: LinkedInOutput;
    critiqueTrace: CritiqueTrace;
}

function SFScoreChart({ scores, label }: { scores: ShortFormScores[]; label: string }) {
    const data = scores.map((s, i) => ({
        name: `Draft ${i + 1}`,
        'Hook Density': s.hook_density,
        'Platform Feel': s.platform_native_feel,
        Engagement: s.engagement_trigger_strength,
        Shareability: s.shareability,
        'Brand Fit': s.brand_fit,
    }));

    return (
        <ResponsiveContainer width="100%" height={160}>
            <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <YAxis domain={[0, 10]} tick={{ fill: '#9ca3af', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid rgba(99,102,241,0.3)', borderRadius: 8 }} />
                <Legend wrapperStyle={{ fontSize: 10, color: '#9ca3af' }} />
                <Line type="monotone" dataKey="Hook Density" stroke="#818cf8" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Platform Feel" stroke="#34d399" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Engagement" stroke="#c084fc" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Shareability" stroke="#fb923c" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="Brand Fit" stroke="#f472b6" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
        </ResponsiveContainer>
    );
}

export default function LinkedInOutputPanel({ data, critiqueTrace }: Props) {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(data.final_draft);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const paragraphs = data.final_draft.split('\n').filter(l => l.trim() !== '');

    return (
        <section className="panel space-y-5">
            <div className="flex items-center justify-between">
                <p className="panel-title mb-0">LinkedIn Output</p>
                <button onClick={handleCopy} className="copy-btn">
                    {copied ? '✓ Copied' : '⎘ Copy Post'}
                </button>
            </div>

            {/* Score Chart */}
            {critiqueTrace.linkedin_scores_by_draft.length > 0 && (
                <div className="rounded-xl bg-gray-900/60 border border-gray-700/50 p-4">
                    <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Score Evolution</p>
                    <SFScoreChart scores={critiqueTrace.linkedin_scores_by_draft} label="LinkedIn" />
                </div>
            )}

            {/* LinkedIn Post Preview */}
            <div className="rounded-xl bg-gray-900/60 border border-gray-700/50 p-5">
                {/* Simulated LinkedIn card */}
                <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold shrink-0">
                        DV
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-white">DataVex</p>
                        <p className="text-xs text-gray-500">B2B Data Intelligence · Following</p>
                    </div>
                </div>
                <div className="space-y-2 text-sm text-gray-300 leading-relaxed">
                    {paragraphs.map((p, i) => (
                        <p key={i} className={i === 0 ? 'font-semibold text-white' : ''}>
                            {p}
                        </p>
                    ))}
                </div>
                <div className="mt-4 pt-4 border-t border-gray-800 flex gap-4 text-xs text-gray-600">
                    <span>👍 Like</span>
                    <span>💬 Comment</span>
                    <span>♻ Repost</span>
                    <span>📤 Send</span>
                </div>
            </div>
        </section>
    );
}
