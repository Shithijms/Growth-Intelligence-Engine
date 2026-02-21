'use client';

import React, { useState, useCallback } from 'react';
import { PipelineOutput, ProgressEvent, PipelineStage } from '@/lib/types';
import { runPipelineStream } from '@/lib/api';
import KeywordInput from '@/components/panels/KeywordInput';
import SignalReport from '@/components/panels/SignalReport';
import StrategyBriefPanel from '@/components/panels/StrategyBriefPanel';
import BlogOutputPanel from '@/components/panels/BlogOutputPanel';
import LinkedInOutputPanel from '@/components/panels/LinkedInOutputPanel';
import TwitterOutputPanel from '@/components/panels/TwitterOutputPanel';
import CritiqueTracePanel from '@/components/panels/CritiqueTracePanel';
import QualityGatePanel from '@/components/panels/QualityGatePanel';

const PIPELINE_STAGES: PipelineStage[] = [
    { id: 'discover_signals', label: 'Signal Discovery', completed: false, active: false },
    { id: 'score_signals', label: 'Signal Scoring', completed: false, active: false },
    { id: 'validate_signal', label: 'Signal Validation', completed: false, active: false },
    { id: 'scan_serp', label: 'SERP Analysis', completed: false, active: false },
    { id: 'strategy_brief', label: 'Strategy Brief', completed: false, active: false },
    { id: 'blog_draft_1', label: 'Blog Draft 1', completed: false, active: false },
    { id: 'blog_critique_1', label: 'Blog Critique 1', completed: false, active: false },
    { id: 'blog_draft_2', label: 'Blog Draft 2', completed: false, active: false },
    { id: 'blog_critique_2', label: 'Blog Critique 2', completed: false, active: false },
    { id: 'blog_gate', label: 'Blog Gate', completed: false, active: false },
    { id: 'short_form_draft_1', label: 'Short Form D1', completed: false, active: false },
    { id: 'short_form_critique_1', label: 'SF Critique 1', completed: false, active: false },
    { id: 'short_form_draft_2', label: 'Short Form D2', completed: false, active: false },
    { id: 'short_form_critique_2', label: 'SF Critique 2', completed: false, active: false },
    { id: 'short_form_gate', label: 'SF Gate', completed: false, active: false },
    { id: 'complete', label: 'Complete', completed: false, active: false },
];

export default function DashboardPage() {
    const [output, setOutput] = useState<PipelineOutput | null>(null);
    const [running, setRunning] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [stages, setStages] = useState<PipelineStage[]>(PIPELINE_STAGES);
    const [currentLabel, setCurrentLabel] = useState<string>('');
    const [keyword, setKeyword] = useState<string>('');

    const updateStage = useCallback((stageId: string) => {
        setStages(prev => {
            const idx = prev.findIndex(s => s.id === stageId);
            if (idx === -1) return prev;
            return prev.map((s, i) => ({
                ...s,
                completed: i < idx,
                active: i === idx,
            }));
        });
    }, []);

    const handleRun = useCallback(async (kw: string) => {
        setKeyword(kw);
        setRunning(true);
        setError(null);
        setOutput(null);
        setStages(PIPELINE_STAGES.map(s => ({ ...s, completed: false, active: false })));
        setCurrentLabel('Starting pipeline...');

        try {
            await runPipelineStream(
                kw,
                (event: ProgressEvent) => {
                    setCurrentLabel(event.label);
                    updateStage(event.stage);
                },
                (result: PipelineOutput) => {
                    setOutput(result);
                    setStages(PIPELINE_STAGES.map(s => ({ ...s, completed: true, active: false })));
                    setCurrentLabel('Pipeline complete!');
                },
                (err: string) => {
                    setError(err);
                    setCurrentLabel('');
                },
            );
        } catch (e: unknown) {
            const msg = e instanceof Error ? e.message : 'Unexpected error';
            setError(msg);
        } finally {
            setRunning(false);
        }
    }, [updateStage]);

    const handleExport = useCallback(() => {
        if (!output) return;
        const blob = new Blob([JSON.stringify(output, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `datavex-pipeline-${keyword.replace(/\s+/g, '-')}-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }, [output, keyword]);

    const completedCount = stages.filter(s => s.completed).length;
    const progressPct = running || output ? Math.round((completedCount / stages.length) * 100) : 0;

    return (
        <div className="min-h-screen bg-[rgb(5,6,15)]">
            {/* Header */}
            <header className="border-b border-gray-800/60 bg-[rgb(7,8,20)]/80 backdrop-blur sticky top-0 z-50">
                <div className="max-w-screen-2xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                            <span className="text-white font-bold text-sm">DV</span>
                        </div>
                        <div>
                            <h1 className="font-bold text-white text-sm tracking-tight">DataVex</h1>
                            <p className="text-xs text-gray-500">Growth Intelligence Engine</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        {output && (
                            <div className="text-xs text-gray-500">
                                Completed in{' '}
                                <span className="text-indigo-400 font-medium">
                                    {output.run_metadata.total_pipeline_duration_seconds}s
                                </span>
                            </div>
                        )}
                        {output && (
                            <button
                                onClick={handleExport}
                                className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium
                           bg-indigo-600/20 text-indigo-300 border border-indigo-600/30
                           hover:bg-indigo-600/40 transition-all"
                            >
                                ↓ Export JSON
                            </button>
                        )}
                    </div>
                </div>
            </header>

            <main className="max-w-screen-2xl mx-auto px-6 py-8 space-y-6">
                {/* Panel 1 — Input */}
                <KeywordInput
                    onRun={handleRun}
                    running={running}
                    stages={stages}
                    currentLabel={currentLabel}
                    progressPct={progressPct}
                    error={error}
                />

                {/* Output panels — only rendered when data exists */}
                {output && (
                    <>
                        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                            {/* Panel 2 */}
                            <SignalReport data={output.signal_report} />
                            {/* Panel 3 */}
                            <StrategyBriefPanel data={output.strategy_brief} />
                        </div>

                        {/* Panel 4 */}
                        <BlogOutputPanel data={output.blog} critiqueTrace={output.critique_trace} />

                        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                            {/* Panel 5 */}
                            <LinkedInOutputPanel data={output.linkedin} critiqueTrace={output.critique_trace} />
                            {/* Panel 6 */}
                            <TwitterOutputPanel data={output.twitter_thread} critiqueTrace={output.critique_trace} />
                        </div>

                        {/* Panel 7 */}
                        <CritiqueTracePanel
                            blog={output.blog}
                            linkedin={output.linkedin}
                            twitter={output.twitter_thread}
                            critiqueTrace={output.critique_trace}
                        />

                        {/* Panel 8 */}
                        <QualityGatePanel gates={output.quality_gate_log} />
                    </>
                )}
            </main>
        </div>
    );
}
