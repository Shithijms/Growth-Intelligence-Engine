'use client';

import React from 'react';
import { GateDecision } from '@/lib/types';

interface Props {
    gates: GateDecision[];
}

export default function QualityGatePanel({ gates }: Props) {
    if (!gates || gates.length === 0) {
        return (
            <section className="panel">
                <p className="panel-title">Quality Gate Log</p>
                <p className="text-sm text-gray-600">No gate decisions recorded.</p>
            </section>
        );
    }

    return (
        <section className="panel space-y-4">
            <p className="panel-title">Quality Gate Log</p>

            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-gray-800">
                            <th className="text-left py-3 pr-6 text-xs font-medium text-gray-500 uppercase tracking-wider">Asset</th>
                            <th className="text-left py-3 pr-6 text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th className="text-left py-3 pr-6 text-xs font-medium text-gray-500 uppercase tracking-wider">Trigger Reason</th>
                            <th className="text-left py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Scores</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800/60">
                        {gates.map((g, i) => (
                            <tr key={i} className="hover:bg-gray-900/30 transition-colors">
                                <td className="py-3 pr-6">
                                    <span className="capitalize font-medium text-white">{g.asset}</span>
                                </td>
                                <td className="py-3 pr-6">
                                    {g.gate_passed ? (
                                        <span className="badge-pass">✓ PASS</span>
                                    ) : (
                                        <span className="badge-fail">✗ FAIL</span>
                                    )}
                                </td>
                                <td className="py-3 pr-6">
                                    <span className="text-xs text-gray-400">{g.trigger_reason}</span>
                                </td>
                                <td className="py-3">
                                    <div className="flex flex-wrap gap-1.5">
                                        {Object.entries(g.final_scores).map(([dim, score]) => (
                                            <div key={dim} className="flex items-center gap-1">
                                                <span className="text-xs text-gray-600">{dim.replace(/_/g, ' ')}:</span>
                                                <span className={`text-xs font-mono font-bold ${score >= 7 ? 'text-emerald-400' : 'text-red-400'
                                                    }`}>
                                                    {score.toFixed(1)}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Summary bar */}
            <div className="flex items-center gap-4 px-4 py-3 rounded-xl bg-gray-900/60 border border-gray-700/50">
                <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">Pass:</span>
                    <span className="text-sm font-bold text-emerald-400">
                        {gates.filter(g => g.gate_passed).length}
                    </span>
                </div>
                <div className="w-px h-4 bg-gray-800" />
                <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">Fail:</span>
                    <span className="text-sm font-bold text-red-400">
                        {gates.filter(g => !g.gate_passed).length}
                    </span>
                </div>
                <div className="w-px h-4 bg-gray-800" />
                <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">Total:</span>
                    <span className="text-sm font-bold text-white">{gates.length}</span>
                </div>
            </div>
        </section>
    );
}
