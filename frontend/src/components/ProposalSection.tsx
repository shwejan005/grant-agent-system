"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

interface ProposalSectionProps {
    title: string;
    content: string;
    delay?: number;
}

export default function ProposalSection({
    title,
    content,
    delay = 0,
}: ProposalSectionProps) {
    const [isExpanded, setIsExpanded] = useState(true);

    const formatContent = (text: string) => {
        try {
            const parsed = JSON.parse(text);
            if (Array.isArray(parsed)) {
                return parsed.map((item, i) => (
                    <div key={i} className="flex gap-3 mb-3 bg-white/40 p-4 rounded-xl border border-border/30">
                        <span className="text-muted font-bold text-xs mt-0.5">{(i + 1).toString().padStart(2, '0')}</span>
                        <span className="text-sm font-medium leading-relaxed text-foreground">
                            {typeof item === 'string' ? item : JSON.stringify(item)}
                        </span>
                    </div>
                ));
            }
        } catch {
            // Not JSON, render as text
        }

        return text.split("\n").map((line, i) => (
            <p key={i} className={line.trim() === "" ? "h-4" : "mb-3 text-[15px] font-medium leading-relaxed text-foreground/85"}>
                {line}
            </p>
        ));
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
            className="bg-white/50 backdrop-blur-sm rounded-3xl border border-white shadow-sm overflow-hidden"
        >
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center justify-between p-6 text-left group transition-colors hover:bg-white/40"
            >
                <h3 className="text-sm font-bold text-foreground uppercase tracking-widest">
                    {title}
                </h3>
                <motion.div
                    animate={{ rotate: isExpanded ? 180 : 0 }}
                    transition={{ duration: 0.3 }}
                    className="w-8 h-8 rounded-full bg-surface-hover flex items-center justify-center group-hover:bg-white transition-colors"
                >
                    <ChevronDown className="w-4 h-4 text-muted" />
                </motion.div>
            </button>

            <AnimatePresence initial={false}>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                        className="overflow-hidden"
                    >
                        <div className="px-6 pb-6 mt-[-8px]">
                            <div className="whitespace-pre-wrap">{formatContent(content)}</div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}
