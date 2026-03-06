"use client";

import { motion, AnimatePresence } from "framer-motion";
import { PipelineResult, PipelineStatus } from "@/lib/types";
import { FileSearch, Sparkles, AlertCircle } from "lucide-react";
import ProposalSection from "./ProposalSection";
import BudgetTable from "./BudgetTable";
import Timeline from "./Timeline";
import SkeletonLoader from "./SkeletonLoader";
import { cn } from "@/lib/utils";
import SpotlightCard from "./SpotlightCard";

interface MainWorkspaceProps {
    pipelineResult: PipelineResult | null;
    pipelineStatus: PipelineStatus | null;
    selectedIteration: number;
    onSelectIteration: (n: number) => void;
    isLoading: boolean;
}

export default function MainWorkspace({
    pipelineResult,
    pipelineStatus,
    selectedIteration,
    onSelectIteration,
    isLoading,
}: MainWorkspaceProps) {
    const currentIteration = pipelineResult?.iterations?.find(
        (it) => it.iteration === selectedIteration
    );

    return (
        <div className="flex-1 z-10 flex flex-col min-w-0">
            <SpotlightCard className="flex-1 flex flex-col p-0 w-full overflow-hidden">
                <main className="flex-1 overflow-y-auto p-6 md:p-10 custom-scrollbar">

                    {/* Empty State */}
                    {!pipelineResult && !isLoading && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="h-full flex flex-col items-center justify-center py-20"
                        >
                            <div className="w-20 h-20 bg-white/50 backdrop-blur-md rounded-3xl flex items-center justify-center mb-6 shadow-2xl shadow-black/5 border border-white">
                                <FileSearch className="w-8 h-8 text-muted" />
                            </div>
                            <h2 className="text-2xl font-bold text-foreground mb-3 text-center">
                                Awaiting Directives
                            </h2>
                            <p className="text-base text-muted text-center max-w-sm leading-relaxed">
                                The AI is standing by. Select your parameters on the left and initialize the generation sequence.
                            </p>
                        </motion.div>
                    )}

                    {/* Loading State */}
                    {isLoading && !pipelineResult && (
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="max-w-4xl mx-auto space-y-8"
                        >
                            <div className="flex items-center gap-4 bg-white/40 border border-border/50 rounded-2xl p-6 shadow-sm">
                                <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center border border-indigo-100">
                                    <Sparkles className="w-6 h-6 text-indigo-500 animate-pulse" />
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-sm font-bold text-foreground">
                                        {pipelineStatus?.message || "Orchestrating AI Agents..."}
                                    </h3>
                                    <div className="flex items-center gap-3 mt-1 text-xs font-semibold uppercase tracking-wider text-muted">
                                        <span>Stage: {pipelineStatus?.stage || "init"}</span>
                                        <span className="w-1 h-1 bg-border-dark rounded-full" />
                                        <span>Iteration {pipelineStatus?.iteration || 0} / {pipelineStatus?.max_iterations || "–"}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-6">
                                <SkeletonLoader />
                                <SkeletonLoader />
                                <SkeletonLoader />
                            </div>
                        </motion.div>
                    )}

                    {/* Results State */}
                    {pipelineResult && (
                        <div className="max-w-4xl mx-auto">
                            {/* Minimal Iteration Switcher */}
                            <div className="flex items-center justify-between mb-10 pb-6 border-b border-border/40 sticky top-0 bg-surface/80 backdrop-blur-xl z-30 -mx-6 px-6 -mt-6 pt-6">
                                <div className="flex items-center gap-1 bg-white/40 p-1.5 rounded-2xl border border-border/60 shadow-sm">
                                    {pipelineResult.iterations.map((it) => (
                                        <button
                                            key={it.iteration}
                                            onClick={() => onSelectIteration(it.iteration)}
                                            className={cn(
                                                "px-5 py-2 text-sm font-bold rounded-xl transition-all duration-300",
                                                selectedIteration === it.iteration
                                                    ? "bg-foreground text-white shadow-md shadow-foreground/20"
                                                    : "text-muted hover:text-foreground hover:bg-white/50"
                                            )}
                                        >
                                            v{it.iteration}
                                        </button>
                                    ))}
                                </div>

                                {pipelineResult.total_iterations > 1 && (
                                    <div className="flex items-center gap-2 bg-success/10 text-success-700 px-4 py-2 rounded-2xl font-bold text-sm">
                                        <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
                                        Score: {pipelineResult.score_history[selectedIteration - 1]?.toFixed(1)}
                                    </div>
                                )}
                            </div>

                            <AnimatePresence mode="wait">
                                <motion.div
                                    key={selectedIteration}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                                    className="pb-20"
                                >
                                    {currentIteration?.proposal && (
                                        <div className="space-y-8">
                                            {/* Hero Title */}
                                            <div className="mb-12">
                                                <h1 className="text-3xl md:text-5xl font-bold text-foreground leading-tight tracking-tight mb-6">
                                                    {currentIteration.proposal.title}
                                                </h1>

                                                <div className="bg-white/60 p-6 rounded-3xl border border-white shadow-xl shadow-black/5">
                                                    <h3 className="text-xs font-bold text-muted uppercase tracking-widest mb-3">Abstract</h3>
                                                    <p className="text-base text-foreground/80 leading-relaxed font-medium">
                                                        {currentIteration.proposal.abstract}
                                                    </p>
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-1 gap-6">
                                                <ProposalSection
                                                    title="Background & Problem"
                                                    content={currentIteration.proposal.background}
                                                    delay={0.1}
                                                />
                                                <ProposalSection
                                                    title="Core Objectives"
                                                    content={
                                                        typeof currentIteration.proposal.objectives === "string"
                                                            ? currentIteration.proposal.objectives
                                                            : JSON.stringify(currentIteration.proposal.objectives, null, 2)
                                                    }
                                                    delay={0.2}
                                                />
                                                <ProposalSection
                                                    title="Methodology & Approach"
                                                    content={currentIteration.proposal.methodology}
                                                    delay={0.3}
                                                />
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                    <ProposalSection
                                                        title="Expected Impact"
                                                        content={currentIteration.proposal.expected_impact}
                                                        delay={0.4}
                                                    />
                                                    <ProposalSection
                                                        title="Deliverables"
                                                        content={
                                                            typeof currentIteration.proposal.deliverables === "string"
                                                                ? currentIteration.proposal.deliverables
                                                                : JSON.stringify(currentIteration.proposal.deliverables, null, 2)
                                                        }
                                                        delay={0.5}
                                                    />
                                                </div>
                                            </div>

                                            {/* Financial & Timeline */}
                                            <div className="pt-8 mt-8 border-t border-border/40 grid grid-cols-1 xl:grid-cols-2 gap-8">
                                                {currentIteration.budget && (
                                                    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.6 }}>
                                                        <h3 className="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
                                                            Financial Plan
                                                        </h3>
                                                        <BudgetTable budget={currentIteration.budget} />
                                                    </motion.div>
                                                )}

                                                {currentIteration.budget?.milestone_schedule && (
                                                    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.7 }}>
                                                        <h3 className="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
                                                            Execution Timeline
                                                        </h3>
                                                        <Timeline milestones={currentIteration.budget.milestone_schedule} />
                                                    </motion.div>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </motion.div>
                            </AnimatePresence>
                        </div>
                    )}
                </main>
            </SpotlightCard>
        </div>
    );
}
