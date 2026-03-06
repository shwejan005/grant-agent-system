"use client";

import { motion } from "framer-motion";
import { PipelineResult, PipelineStatus } from "@/lib/types";
import { Activity, Target, ShieldAlert, GitCommit, CheckCircle2 } from "lucide-react";
import ScoreBar from "./ScoreBar";
import { cn } from "@/lib/utils";
import SpotlightCard from "./SpotlightCard";

interface RightPanelProps {
    pipelineResult: PipelineResult | null;
    pipelineStatus: PipelineStatus | null;
    selectedIteration: number;
    isLoading: boolean;
}

export default function RightPanel({
    pipelineResult,
    pipelineStatus,
    selectedIteration,
    isLoading,
}: RightPanelProps) {
    const currentIteration = pipelineResult?.iterations?.find(
        (it) => it.iteration === selectedIteration
    );
    const evaluation = currentIteration?.evaluation;

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="w-[340px] flex-shrink-0 z-20 flex flex-col"
        >
            <SpotlightCard className="flex-1 flex flex-col p-0 w-full overflow-hidden">
                <aside className="p-6 flex-1 overflow-y-auto space-y-8 custom-scrollbar">

                    <div className="flex items-center gap-2 mb-2">
                        <Activity className="w-5 h-5 text-foreground" />
                        <h2 className="text-lg font-bold text-foreground tracking-tight">Intelligence</h2>
                    </div>

                    {/* Empty State */}
                    {!pipelineResult && !isLoading && (
                        <div className="bg-white/40 rounded-2xl border border-border/50 p-8 text-center mt-10">
                            <Target className="w-8 h-8 text-muted/50 mx-auto mb-4" />
                            <p className="text-sm text-muted font-medium">Evaluation matrix offline. Awaiting proposal generation.</p>
                        </div>
                    )}

                    {/* Loading State */}
                    {isLoading && !evaluation && (
                        <div className="space-y-6 mt-6">
                            <div className="h-32 bg-white/40 rounded-3xl border border-border/50 animate-pulse" />
                            <div className="space-y-4">
                                {[...Array(4)].map((_, i) => (
                                    <div key={i} className="flex gap-3">
                                        <div className="w-8 h-8 rounded-full bg-white/40 animate-pulse block flex-shrink-0" />
                                        <div className="flex-1 space-y-2 py-1">
                                            <div className="h-2 w-1/2 bg-border-dark/30 rounded-full animate-pulse" />
                                            <div className="h-1.5 w-full bg-border-dark/20 rounded-full animate-pulse" />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Results Overview */}
                    {evaluation && (
                        <motion.div
                            initial={{ opacity: 0, filter: "blur(5px)" }}
                            animate={{ opacity: 1, filter: "blur(0px)" }}
                            transition={{ duration: 0.5 }}
                            className="space-y-8"
                        >
                            {/* Massive Hero Score */}
                            <div className="text-center relative">
                                <div className="absolute inset-0 bg-brand-purple blur-[40px] opacity-10 rounded-full" />
                                <motion.div
                                    initial={{ scale: 0.8, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    transition={{ type: "spring", stiffness: 200, damping: 20 }}
                                    className="relative z-10"
                                >
                                    <div className="text-[5rem] font-bold text-foreground leading-none tracking-tighter">
                                        {evaluation.total_score.toFixed(1)}
                                    </div>
                                    <div className="text-sm font-bold text-muted uppercase tracking-widest mt-1">
                                        Overall Score
                                    </div>
                                </motion.div>
                            </div>

                            {/* Micro Progression Chart */}
                            {pipelineResult && pipelineResult.score_history.length > 1 && (
                                <div className="bg-white/50 rounded-2xl p-4 border border-white shadow-sm">
                                    <div className="flex items-end justify-between h-12 gap-1.5">
                                        {pipelineResult.score_history.map((score, i) => {
                                            const isSelected = i + 1 === selectedIteration;
                                            return (
                                                <motion.div
                                                    key={i}
                                                    initial={{ height: 0 }}
                                                    animate={{ height: `${(score / 10) * 100}%` }}
                                                    className={cn(
                                                        "flex-1 rounded-sm transition-all duration-300 relative group",
                                                        isSelected ? "bg-foreground" : "bg-border-dark/60 hover:bg-muted"
                                                    )}
                                                >
                                                    <div className="absolute -top-6 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 text-[10px] font-bold text-foreground transition-opacity">
                                                        {score.toFixed(1)}
                                                    </div>
                                                </motion.div>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Evaluation Rubric Details */}
                            <div className="space-y-4">
                                <h3 className="text-xs font-bold text-foreground uppercase tracking-widest flex items-center gap-2">
                                    <ShieldAlert className="w-4 h-4 text-muted" />
                                    Rubric Analysis
                                </h3>
                                <div className="bg-white/40 border border-white shadow-sm rounded-3xl p-5 space-y-6">
                                    {evaluation.rubric_breakdown &&
                                        Object.entries(evaluation.rubric_breakdown).map(
                                            ([key, detail], index) => (
                                                <ScoreBar
                                                    key={key}
                                                    label={key
                                                        .replace(/^(rule_|llm_)/, "")
                                                        .replace(/_/g, " ")}
                                                    score={typeof detail === 'object' && detail !== null ? (detail as { score: number }).score : 0}
                                                    maxScore={typeof detail === 'object' && detail !== null ? (detail as { max_score: number }).max_score : 10}
                                                    feedback={typeof detail === 'object' && detail !== null ? (detail as { feedback: string }).feedback : ''}
                                                    delay={index * 0.1}
                                                    variant={key.startsWith("rule_") ? "rule" : "llm"}
                                                />
                                            )
                                        )}
                                </div>
                            </div>

                            {/* Critique Report */}
                            {evaluation.critique_report && (
                                <div className="bg-amber-50/50 border border-amber-200/50 rounded-2xl p-5">
                                    <p className="text-[13px] text-amber-900 leading-relaxed font-medium">
                                        {evaluation.critique_report}
                                    </p>
                                </div>
                            )}

                            {/* Strengths & Weaknesses tags */}
                            {(evaluation.strengths || evaluation.weaknesses) && (
                                <div className="grid grid-cols-1 gap-4">
                                    {evaluation.strengths && evaluation.strengths.length > 0 && (
                                        <div>
                                            <h4 className="text-[10px] font-bold text-emerald-700 uppercase tracking-widest mb-2 flex items-center gap-1">
                                                <CheckCircle2 className="w-3 h-3" /> Exceeds
                                            </h4>
                                            <div className="flex flex-wrap gap-1.5">
                                                {evaluation.strengths.map((s, i) => (
                                                    <span key={i} className="text-[11px] font-medium bg-emerald-100/50 text-emerald-800 px-2 py-1 rounded-md border border-emerald-200">
                                                        {s}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {evaluation.weaknesses && evaluation.weaknesses.length > 0 && (
                                        <div>
                                            <h4 className="text-[10px] font-bold text-red-700 uppercase tracking-widest mb-2 flex items-center gap-1">
                                                <Target className="w-3 h-3" /> Gaps
                                            </h4>
                                            <div className="flex flex-wrap gap-1.5">
                                                {evaluation.weaknesses.map((w, i) => (
                                                    <span key={i} className="text-[11px] font-medium bg-red-100/50 text-red-800 px-2 py-1 rounded-md border border-red-200">
                                                        {w}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Agent Refinement Log */}
                            {currentIteration?.refinement && (
                                <div className="pt-6 border-t border-border/40">
                                    <h3 className="text-xs font-bold text-foreground uppercase tracking-widest mb-4 flex items-center gap-2">
                                        <GitCommit className="w-4 h-4 text-muted" />
                                        Delta Log
                                    </h3>
                                    <div className="space-y-3">
                                        {currentIteration.refinement.change_summary.map((change, i) => (
                                            <motion.div
                                                key={i}
                                                className="text-xs bg-white/30 border border-white p-3 rounded-xl shadow-sm"
                                                initial={{ opacity: 0, x: -10 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: 0.5 + (i * 0.1) }}
                                            >
                                                <span className="font-bold text-foreground block mb-0.5">
                                                    {change.section}
                                                </span>
                                                <span className="text-muted leading-relaxed font-medium">
                                                    {change.change}
                                                </span>
                                            </motion.div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    )}
                </aside>
            </SpotlightCard>
        </motion.div>
    );
}
