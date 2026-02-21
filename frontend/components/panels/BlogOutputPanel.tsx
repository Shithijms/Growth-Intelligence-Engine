'use client';

import React, { useState } from 'react';
import { BlogOutput, CritiqueTrace, BlogScores } from '@/lib/types';
import ReactMarkdown from 'react-markdown';
import {
    RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
    LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid,
} from 'recharts';

interface Props {
    data: BlogOutput;
    critiqueTrace: CritiqueTrace;
}

function ScoreEvolutionChart({ scores }: { scores: BlogScores[] }) {
    const data = scores.map((s, i) => ({
        name: `Draft ${i + 1}`,
        Hook: s.hook_strength,
        Clarity: s.clarity,
        Authority: s.authority_tone,
        Differentiation: s.differentiation,
        Structure: s.logical_structure,
        'Brand Fit': s.datavex_brand_fit,
    }));

    return (
        <ResponsiveContainer width="100%" height={200}>
            <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                <YAxis domain={[0, 10]} tick={{ fill: '#9ca3af', fontSize: 11 }} />
                <Tooltip
                    contentStyle={{ background: '#111827', border: '1px solid rgba(99,102,241,0.3)', borderRadius: 8 }}
                    labelStyle={{ color: '#e5e7eb' }}
                />
                <Legend wrapperStyle={{ fontSize: 11, color: '#9ca3af' }} />
                <Line type="monotone" dataKey="Hook" stroke="#818cf8" strokeWidth={2} dot={{ r: 4, fill: '#818cf8' }} />
                <Line type="monotone" dataKey="Clarity" stroke="#34d399" strokeWidth={2} dot={{ r: 4, fill: '#34d399' }} />
                <Line type="monotone" dataKey="Authority" stroke="#c084fc" strokeWidth={2} dot={{ r: 4, fill: '#c084fc' }} />
                <Line type="monotone" dataKey="Differentiation" stroke="#fb923c" strokeWidth={2} dot={{ r: 4, fill: '#fb923c' }} />
                <Line type="monotone" dataKey="Structure" stroke="#38bdf8" strokeWidth={2} dot={{ r: 4, fill: '#38bdf8' }} />
                <Line type="monotone" dataKey="Brand Fit" stroke="#f472b6" strokeWidth={2} dot={{ r: 4, fill: '#f472b6' }} />
            </LineChart>
        </ResponsiveContainer>
    );
}

export default function BlogOutputPanel({ data, critiqueTrace }: Props) {
    const [copied, setCopied] = useState(false);
    const [activeTab, setActiveTab] = useState<'preview' | 'raw'>('preview');

    const handleCopy = () => {
        navigator.clipboard.writeText(data.final_draft);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <section className="panel space-y-5">
            <div className="flex items-center justify-between">
                <p className="panel-title mb-0">Blog Output</p>
                <button onClick={handleCopy} className="copy-btn">
                    {copied ? '✓ Copied' : '⎘ Copy Markdown'}
                </button>
            </div>

            {/* Meta */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="rounded-xl bg-gray-900/60 border border-gray-700/50 p-3 space-y-1">
                    <p className="text-xs text-gray-600 uppercase tracking-wider">Meta Title</p>
                    <p className="text-sm text-white font-medium">{data.meta_title}</p>
                </div>
                <div className="rounded-xl bg-gray-900/60 border border-gray-700/50 p-3 space-y-1">
                    <p className="text-xs text-gray-600 uppercase tracking-wider">Meta Description</p>
                    <p className="text-xs text-gray-300">{data.meta_description}</p>
                </div>
            </div>

            {/* Score Evolution Chart */}
            {critiqueTrace.blog_scores_by_draft.length > 0 && (
                <div className="rounded-xl bg-gray-900/60 border border-gray-700/50 p-4">
                    <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Score Evolution</p>
                    <ScoreEvolutionChart scores={critiqueTrace.blog_scores_by_draft} />
                </div>
            )}

            {/* Blog Preview */}
            <div className="rounded-xl bg-gray-900/60 border border-gray-700/50 overflow-hidden">
                <div className="flex border-b border-gray-800">
                    {(['preview', 'raw'] as const).map(tab => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-4 py-2.5 text-xs font-medium capitalize transition-colors ${activeTab === tab
                                    ? 'text-indigo-400 border-b-2 border-indigo-500 bg-indigo-500/5'
                                    : 'text-gray-500 hover:text-gray-300'
                                }`}
                        >
                            {tab}
                        </button>
                    ))}
                </div>
                <div className="p-6 max-h-[500px] overflow-y-auto">
                    {activeTab === 'preview' ? (
                        <div className="prose prose-invert prose-sm max-w-none
                            prose-headings:text-white prose-headings:font-bold
                            prose-p:text-gray-300 prose-p:leading-relaxed
                            prose-a:text-indigo-400 prose-strong:text-white
                            prose-li:text-gray-300">
                            <ReactMarkdown>{data.final_draft}</ReactMarkdown>
                        </div>
                    ) : (
                        <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono leading-relaxed">
                            {data.final_draft}
                        </pre>
                    )}
                </div>
            </div>
        </section>
    );
}
