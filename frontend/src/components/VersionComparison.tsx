"use client";

import { motion } from "framer-motion";
import { PipelineResult } from "@/lib/types";

interface VersionComparisonProps {
    pipelineResult: PipelineResult;
    iterationA: number;
    iterationB: number;
}

export default function VersionComparison({
    pipelineResult,
    iterationA,
    iterationB,
}: VersionComparisonProps) {
    const proposalA = pipelineResult.iterations.find(
        (it) => it.iteration === iterationA
    )?.proposal;
    const proposalB = pipelineResult.iterations.find(
        (it) => it.iteration === iterationB
    )?.proposal;

    if (!proposalA || !proposalB) return null;

    const sections = [
        { key: "title", label: "Title" },
        { key: "abstract", label: "Abstract" },
        { key: "background", label: "Background" },
        { key: "objectives", label: "Objectives" },
        { key: "methodology", label: "Methodology" },
        { key: "expected_impact", label: "Expected Impact" },
        { key: "deliverables", label: "Deliverables" },
    ] as const;

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
        >
            <div className="flex items-center gap-4 text-xs font-bold text-muted uppercase tracking-widest bg-white/40 p-3 rounded-2xl border border-white/60 shadow-sm">
                <div className="flex-1 text-center bg-surface py-2 rounded-xl">
                    Version {iterationA}
                </div>
                <div className="w-8 flex items-center justify-center">
                    <span className="text-muted/50">VS</span>
                </div>
                <div className="flex-1 text-center bg-surface py-2 rounded-xl text-foreground">
                    Version {iterationB}
                </div>
            </div>

            {sections.map(({ key, label }) => {
                const contentA = String((proposalA as Record<string, unknown>)[key] || "");
                const contentB = String((proposalB as Record<string, unknown>)[key] || "");
                const isDifferent = contentA !== contentB;

                return (
                    <div key={key} className="bg-white/50 backdrop-blur-sm border border-white rounded-3xl overflow-hidden shadow-sm">
                        <div className="bg-surface/50 px-6 py-3 border-b border-border/40 flex items-center justify-between">
                            <span className="text-[11px] font-bold text-foreground uppercase tracking-wider">{label}</span>
                            {isDifferent && (
                                <span className="text-[9px] px-2 py-1 bg-brand-orange/10 text-brand-orange border border-brand-orange/20 rounded-md font-bold uppercase tracking-widest shadow-sm">
                                    Modified
                                </span>
                            )}
                        </div>
                        <div className="grid grid-cols-2 divide-x divide-border/40">
                            <div className="p-6 text-[13px] text-foreground/70 leading-relaxed max-h-48 overflow-y-auto custom-scrollbar font-medium">
                                {contentA}
                            </div>
                            <div
                                className={`p-6 text-[13px] leading-relaxed max-h-48 overflow-y-auto custom-scrollbar font-medium relative ${isDifferent ? "text-foreground bg-emerald-50/20" : "text-foreground/70"
                                    }`}
                            >
                                {isDifferent && <div className="absolute inset-0 bg-emerald-500/5 pointer-events-none" />}
                                {contentB}
                            </div>
                        </div>
                    </div>
                );
            })}
        </motion.div>
    );
}
