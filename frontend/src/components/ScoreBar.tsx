"use client";

import { motion } from "framer-motion";
import { Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface ScoreBarProps {
    label: string;
    score: number;
    maxScore: number;
    feedback: string;
    delay?: number;
    variant?: "rule" | "llm";
}

export default function ScoreBar({
    label,
    score,
    maxScore,
    feedback,
    delay = 0,
    variant = "llm",
}: ScoreBarProps) {
    const percentage = (score / maxScore) * 100;

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay, ease: "easeOut" }}
            className="group relative"
        >
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                    <span
                        className={cn(
                            "w-2 h-2 rounded-full shadow-sm",
                            variant === "rule" ? "bg-info shadow-info/40" : "bg-brand-purple shadow-brand-purple/40"
                        )}
                    />
                    <span className="text-xs font-bold text-foreground tracking-wide max-w-[180px] truncate">
                        {label}
                    </span>
                </div>
                <span className="text-[10px] font-bold text-muted bg-surface/80 px-1.5 py-0.5 rounded-md border border-border/50">
                    {score.toFixed(1)} <span className="text-muted/50">/ {maxScore.toFixed(0)}</span>
                </span>
            </div>

            <div className="h-2 bg-border-dark/20 rounded-full overflow-hidden relative">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ duration: 1, delay: delay + 0.2, ease: [0.16, 1, 0.3, 1] }}
                    className={cn(
                        "h-full rounded-full absolute left-0 top-0 bottom-0",
                        percentage >= 80 ? "bg-success" : percentage >= 60 ? "bg-warning" : "bg-danger"
                    )}
                />
            </div>

            {feedback && (
                <div className="mt-2 bg-white/40 p-2.5 rounded-xl border border-white/60 shadow-sm hidden group-hover:flex items-start gap-2 absolute z-30 w-full left-0 origin-top">
                    <Info className="w-4 h-4 text-muted shrink-0 mt-0.5" />
                    <p className="text-[11px] font-medium leading-relaxed text-foreground/80">
                        {feedback}
                    </p>
                </div>
            )}
        </motion.div>
    );
}
