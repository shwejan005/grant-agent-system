"use client";

import { motion } from "framer-motion";
import { Grant } from "@/lib/types";
import { DownloadCloud, RefreshCw, FileText, Settings2, PlayCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import SpotlightCard from "./SpotlightCard";

interface LeftPanelProps {
    grants: Grant[];
    selectedGrant: Grant | null;
    onSelectGrant: (grant: Grant) => void;
    topic: string;
    onTopicChange: (topic: string) => void;
    maxIterations: number;
    onMaxIterationsChange: (n: number) => void;
    onScrape: () => void;
    onStart: () => void;
    isScraping: boolean;
    isLoading: boolean;
}

export default function LeftPanel({
    grants,
    selectedGrant,
    onSelectGrant,
    topic,
    onTopicChange,
    maxIterations,
    onMaxIterationsChange,
    onScrape,
    onStart,
    isScraping,
    isLoading,
}: LeftPanelProps) {
    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="w-80 flex-shrink-0 z-20 flex flex-col"
        >
            <SpotlightCard className="flex-1 flex flex-col p-0 w-full overflow-hidden">
                <aside className="p-6 flex-1 overflow-y-auto space-y-8 custom-scrollbar">

                    {/* Scrape Section */}
                    <section>
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xs font-bold text-foreground uppercase tracking-widest flex items-center gap-2">
                                <DownloadCloud className="w-4 h-4 text-muted" />
                                Programs
                            </h2>
                            <button
                                onClick={onScrape}
                                disabled={isScraping}
                                className="text-muted hover:text-foreground transition-all disabled:opacity-50"
                                title="Refresh Programs"
                            >
                                <RefreshCw className={cn("w-4 h-4", isScraping && "animate-spin")} />
                            </button>
                        </div>

                        {grants.length === 0 ? (
                            <div className="bg-surface/50 rounded-2xl border border-border/50 p-6 text-center">
                                <p className="text-sm text-muted mb-4 font-medium">No programs loaded</p>
                                <button
                                    onClick={onScrape}
                                    disabled={isScraping}
                                    className="w-full py-2.5 bg-foreground text-white text-sm font-semibold rounded-xl hover:bg-zinc-800 transition-all disabled:opacity-50 shadow-md"
                                >
                                    {isScraping ? "Fetching..." : "Scrape SERB"}
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {grants.map((grant, index) => (
                                    <motion.button
                                        key={grant.id}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: index * 0.05 }}
                                        onClick={() => onSelectGrant(grant)}
                                        className={cn(
                                            "w-full text-left p-4 rounded-2xl border transition-all duration-300 relative overflow-hidden group",
                                            selectedGrant?.id === grant.id
                                                ? "border-foreground bg-white/60 shadow-md"
                                                : "border-border/60 hover:border-border-dark hover:bg-white/40"
                                        )}
                                    >
                                        {selectedGrant?.id === grant.id && (
                                            <motion.div layoutId="activeGrantIndicator" className="absolute left-0 top-0 bottom-0 w-1 bg-foreground" />
                                        )}
                                        <p className="text-sm font-bold text-foreground leading-snug mb-1">
                                            {grant.program_name}
                                        </p>
                                        <p className="text-xs text-muted line-clamp-2 leading-relaxed">
                                            {grant.description.slice(0, 80)}...
                                        </p>
                                    </motion.button>
                                ))}
                            </div>
                        )}
                    </section>

                    {/* Research Topic Section */}
                    <section>
                        <h2 className="text-xs font-bold text-foreground uppercase tracking-widest mb-4 flex items-center gap-2">
                            <FileText className="w-4 h-4 text-muted" />
                            Research Topic
                        </h2>
                        <textarea
                            value={topic}
                            onChange={(e) => onTopicChange(e.target.value)}
                            placeholder="Type your research topic here..."
                            rows={4}
                            className="w-full px-4 py-3 text-sm border border-border/60 rounded-2xl bg-white/40 focus:bg-white/70 focus:outline-none focus:ring-2 focus:ring-foreground/20 focus:border-foreground/30 placeholder:text-muted/50 resize-none transition-all shadow-inner"
                        />
                    </section>

                    {/* Settings Section */}
                    <section>
                        <h2 className="text-xs font-bold text-foreground uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Settings2 className="w-4 h-4 text-muted" />
                            Config
                        </h2>
                        <div className="bg-white/40 border border-border/60 rounded-2xl p-4">
                            <div className="flex justify-between items-center mb-3">
                                <label className="text-xs font-semibold text-muted">Max Iterations</label>
                                <span className="text-xs font-bold bg-foreground text-white px-2 py-0.5 rounded-md">
                                    {maxIterations}
                                </span>
                            </div>
                            <input
                                type="range"
                                min={1}
                                max={5}
                                value={maxIterations}
                                onChange={(e) => onMaxIterationsChange(Number(e.target.value))}
                                className="w-full h-1.5 bg-border rounded-full appearance-none cursor-pointer accent-foreground"
                            />
                        </div>
                    </section>
                </aside>

                {/* Floating Start Action */}
                <div className="p-4 bg-gradient-to-t from-background via-background/80 to-transparent border-t border-border/10">
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={onStart}
                        disabled={isLoading || !selectedGrant || !topic.trim()}
                        className="w-full py-4 px-4 bg-foreground text-white text-sm font-bold rounded-2xl hover:bg-zinc-800 transition-all disabled:opacity-40 disabled:scale-100 flex items-center justify-center gap-2 shadow-xl shadow-foreground/20"
                    >
                        {isLoading ? (
                            <RefreshCw className="w-5 h-5 animate-spin" />
                        ) : (
                            <>
                                <PlayCircle className="w-5 h-5 fill-white text-foreground" />
                                Execute Pipeline
                            </>
                        )}
                    </motion.button>
                </div>
            </SpotlightCard>
        </motion.div>
    );
}
