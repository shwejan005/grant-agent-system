"use client";

import { motion } from "framer-motion";
import { Milestone } from "@/lib/types";
import { Map } from "lucide-react";

interface TimelineProps {
    milestones: Milestone[];
}

export default function Timeline({ milestones }: TimelineProps) {
    if (!milestones || milestones.length === 0) return null;

    const maxMonth = Math.max(...milestones.map((m) => m.end_month));

    return (
        <div className="bg-white/50 backdrop-blur-md rounded-3xl border border-white shadow-xl shadow-foreground/5 overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-white/50 bg-white/30">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-white border border-border flex items-center justify-center shadow-sm">
                        <Map className="w-5 h-5 text-foreground" />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-foreground">Timeline Mapping</h3>
                        <p className="text-[11px] font-medium text-muted uppercase tracking-widest mt-0.5">Execution Plan</p>
                    </div>
                </div>
                <div className="text-right">
                    <span className="text-[10px] uppercase font-bold text-muted block mb-1">Duration</span>
                    <span className="text-sm font-bold bg-muted/10 text-foreground px-3 py-1 rounded-xl">
                        {maxMonth} Months
                    </span>
                </div>
            </div>

            <div className="p-6 space-y-5">
                {milestones.map((milestone, index) => {
                    const startPct = ((milestone.start_month - 1) / maxMonth) * 100;
                    const widthPct =
                        ((milestone.end_month - milestone.start_month + 1) / maxMonth) * 100;

                    return (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1, ease: 'easeOut' }}
                            className="group"
                        >
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-bold text-foreground tracking-tight">
                                    {milestone.milestone}
                                </span>
                                <span className="text-[10px] font-bold text-muted bg-white px-2 py-0.5 rounded-full border border-border/50">
                                    M{milestone.start_month} – M{milestone.end_month}
                                </span>
                            </div>

                            <div className="h-8 bg-surface-hover/40 rounded-xl relative overflow-hidden border border-border/30">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${widthPct}%` }}
                                    transition={{ duration: 0.8, delay: index * 0.15, ease: [0.16, 1, 0.3, 1] }}
                                    style={{ marginLeft: `${startPct}%` }}
                                    className="h-full bg-brand-orange/10 border border-brand-orange/30 rounded-xl flex items-center px-3 shadow-inner"
                                >
                                    <span className="text-[10px] font-bold text-brand-orange truncate mix-blend-multiply">
                                        {milestone.budget_allocation && `₹${milestone.budget_allocation}`}
                                    </span>
                                </motion.div>
                            </div>

                            {milestone.deliverables && milestone.deliverables.length > 0 && (
                                <div className="mt-2 flex flex-wrap gap-1.5 opacity-80 group-hover:opacity-100 transition-opacity">
                                    {milestone.deliverables.map((d, i) => (
                                        <span
                                            key={i}
                                            className="text-[10px] font-medium px-2 py-1 bg-white border border-border/40 rounded-lg text-muted/90 shadow-sm"
                                        >
                                            {d}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}
