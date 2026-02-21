'use client';

import React, { useState } from 'react';
import { PipelineStage } from '@/lib/types';

interface Props {
    onRun: (keyword: string) => void;
    running: boolean;
    stages: PipelineStage[];
    currentLabel: string;
    progressPct: number;
    error: string | null;
}

const SAMPLE_KEYWORDS = ['revenue intelligence', 'data warehouse cost optimization', 'AI in RevOps'];

export default function KeywordInput({
    onRun, running, stages, currentLabel, progressPct, error,
}: Props) {
    const [keyword, setKeyword] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (keyword.trim() && !running) onRun(keyword.trim());
    };

    return (
        <section className="panel glow-indigo">
            <p className="panel-title">Growth Intelligence Engine</p>
            <div className="mb-6">
                <h2 className="text-2xl font-bold gradient-text mb-1">
                    Turn a keyword into content assets
                </h2>
                <p className="text-sm text-gray-400">
                    Signal discovery → strategy → blog + LinkedIn + Twitter — fully automated.
                </p>
            </div>

            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
                <input
                    id="keyword-input"
                    type="text"
                    value={keyword}
                    onChange={e => setKeyword(e.target.value)}
                    placeholder="e.g. revenue intelligence"
                    disabled={running}
                    className="flex-1 px-5 py-3 rounded-xl bg-gray-900 border border-gray-700 text-white
                     placeholder:text-gray-600 focus:outline-none focus:border-indigo-500/60
                     focus:ring-1 focus:ring-indigo-500/30 transition-all text-sm disabled:opacity-50"
                />
                <button
                    id="run-pipeline-btn"
                    type="submit"
                    disabled={running || !keyword.trim()}
                    className="px-8 py-3 rounded-xl font-semibold text-sm
                     bg-gradient-to-r from-indigo-600 to-purple-600
                     hover:from-indigo-500 hover:to-purple-500
                     disabled:opacity-40 disabled:cursor-not-allowed
                     transition-all duration-200 shadow-lg shadow-indigo-900/40 text-white"
                >
                    {running ? 'Running...' : 'Run Pipeline'}
                </button>
            </form>

            {/* Sample keywords */}
            <div className="flex flex-wrap gap-2 mt-3">
                <span className="text-xs text-gray-600">Try:</span>
                {SAMPLE_KEYWORDS.map(kw => (
                    <button
                        key={kw}
                        onClick={() => { setKeyword(kw); }}
                        disabled={running}
                        className="text-xs text-indigo-400/70 hover:text-indigo-400 underline underline-offset-2 transition-colors disabled:opacity-40"
                    >
                        {kw}
                    </button>
                ))}
            </div>

            {/* Progress */}
            {(running || progressPct === 100) && (
                <div className="mt-6">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-gray-400">{currentLabel || 'Processing...'}</span>
                        <span className="text-xs font-mono text-indigo-400">{progressPct}%</span>
                    </div>
                    {/* Progress bar */}
                    <div className="score-bar-track">
                        <div
                            className="score-bar-fill bg-gradient-to-r from-indigo-500 to-purple-500"
                            style={{ width: `${progressPct}%` }}
                        />
                    </div>
                    {/* Stage pills */}
                    <div className="flex flex-wrap gap-1.5 mt-3">
                        {stages.map(stage => (
                            <div
                                key={stage.id}
                                className={`px-2 py-0.5 rounded-full text-xs transition-all duration-300 ${stage.completed
                                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                        : stage.active
                                            ? 'bg-indigo-500/30 text-indigo-300 border border-indigo-500/50 animate-pulse'
                                            : 'bg-gray-800/60 text-gray-600 border border-gray-700/50'
                                    }`}
                            >
                                {stage.label}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {error && (
                <div className="mt-4 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                    ⚠ {error}
                </div>
            )}
        </section>
    );
}
