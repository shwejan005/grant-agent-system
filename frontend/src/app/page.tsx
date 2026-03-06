"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Loader2 } from "lucide-react";
import LeftPanel from "@/components/LeftPanel";
import MainWorkspace from "@/components/MainWorkspace";
import RightPanel from "@/components/RightPanel";
import ShinyText from "@/components/ShinyText";
import { fetchGrants, triggerScrape, startPipeline, getPipelineStatus, getPipelineResults } from "@/lib/api";
import { Grant, PipelineStatus, PipelineResult } from "@/lib/types";
import { cn } from "@/lib/utils";

export default function Home() {
  const [grants, setGrants] = useState<Grant[]>([]);
  const [selectedGrant, setSelectedGrant] = useState<Grant | null>(null);
  const [topic, setTopic] = useState("");
  const [maxIterations, setMaxIterations] = useState(3);

  // Pipeline State
  const [isLoading, setIsLoading] = useState(false);
  const [isScraping, setIsScraping] = useState(false);
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null);
  const [pipelineResult, setPipelineResult] = useState<PipelineResult | null>(null);
  const [selectedIteration, setSelectedIteration] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // UI State
  const [hasStarted, setHasStarted] = useState(false);

  const loadGrants = useCallback(async () => {
    try {
      const data = await fetchGrants();
      setGrants(data.grants);
    } catch {
      // It's okay if not scraped yet
    }
  }, []);

  useEffect(() => {
    loadGrants();
  }, [loadGrants]);

  const handleScrape = async () => {
    setIsScraping(true);
    setError(null);
    try {
      await triggerScrape();
      await loadGrants();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scraping failed");
    } finally {
      setIsScraping(false);
    }
  };

  const handleStartPipeline = async () => {
    if (!selectedGrant || !topic.trim()) {
      setError("Please select a grant program and enter a research topic");
      return;
    }

    setHasStarted(true);
    setIsLoading(true);
    setError(null);
    setPipelineResult(null);
    setPipelineStatus(null);
    setSelectedIteration(1);

    try {
      const res = await startPipeline({
        grant_id: selectedGrant.id,
        topic: topic.trim(),
        max_iterations: maxIterations,
      });

      const runId = res.run_id;

      // Poll for status
      pollingRef.current = setInterval(async () => {
        try {
          const status = await getPipelineStatus(runId);
          setPipelineStatus(status);

          if (status.status === "completed" || status.status === "failed") {
            if (pollingRef.current) clearInterval(pollingRef.current);

            if (status.status === "completed") {
              try {
                const results = await getPipelineResults(runId);
                setPipelineResult(results);
                setSelectedIteration(results.total_iterations);
              } catch {
                if (status.result) {
                  setPipelineResult(status.result);
                }
              }
            } else {
              setError("Pipeline failed. Check backend logs for details.");
            }
            setIsLoading(false);
          }
        } catch {
          // Polling error — will retry
        }
      }, 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start pipeline");
      setIsLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  return (
    <div className="min-h-screen relative overflow-hidden flex flex-col font-sans">
      {/* Dynamic Header - Hidden in Grok mode, visible in Dashboard mode */}
      <AnimatePresence>
        {hasStarted && (
          <motion.header
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="h-16 glass-panel border-b border-border/40 z-50 flex-shrink-0"
          >
            <div className="max-w-screen-2xl mx-auto h-full px-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-foreground rounded-lg flex items-center justify-center">
                  <Loader2 className={cn("w-4 h-4 text-white", isLoading && "animate-spin")} />
                </div>
                <div>
                  <h1 className="text-sm font-semibold tracking-tight text-foreground">
                    Grant Proposal Generator
                  </h1>
                </div>
              </div>

              <div className="flex items-center gap-4">
                {pipelineStatus && isLoading && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex items-center gap-2 px-3 py-1.5 glass-panel-heavy rounded-full"
                  >
                    <div className="w-2 h-2 bg-brand-orange rounded-full animate-pulse" />
                    <span className="text-xs font-medium text-foreground">
                      {pipelineStatus.message}
                    </span>
                  </motion.div>
                )}
                {pipelineResult && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex items-center gap-2 px-3 py-1.5 glass-panel-heavy rounded-full"
                  >
                    <div className="w-2 h-2 bg-success rounded-full" />
                    <span className="text-xs font-medium text-foreground">
                      Score: {pipelineResult.final_score.toFixed(1)}/10
                    </span>
                  </motion.div>
                )}
              </div>
            </div>
          </motion.header>
        )}
      </AnimatePresence>

      {/* Main Content Area */}
      <div className={cn(
        "flex-1 flex transition-all duration-700 ease-in-out",
        hasStarted ? "h-[calc(100vh-4rem)]" : "items-center justify-center min-h-screen"
      )}>

        {/* Grok-style Minimal Landing Page */}
        <AnimatePresence>
          {!hasStarted && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9, filter: "blur(10px)", y: -40 }}
              transition={{ duration: 0.5, ease: "easeInOut" }}
              className="w-full max-w-2xl px-6 relative z-10"
            >
              <div className="mb-10 text-center">
                <div className="w-16 h-16 bg-foreground rounded-2xl mx-auto mb-6 flex items-center justify-center shadow-2xl">
                  <Search className="w-8 h-8 text-white" />
                </div>
                <h1 className="text-5xl font-bold tracking-tight text-foreground mb-3 font-sans">
                  Evaluate & <ShinyText text="Generate Proposal" speed={4} className="font-bold text-foreground" />
                </h1>
                <p className="text-base text-muted/80">
                  Select a SERB grant program and describe your research topic.
                </p>
              </div>

              <div className="glass-panel-heavy rounded-3xl p-2 shadow-2xl shadow-foreground/5 transition-all duration-300 focus-within:ring-2 focus-within:ring-foreground/10">
                <div className="flex flex-col sm:flex-row items-center">

                  {/* Grant Selector Dropdown */}
                  <div className="w-full sm:w-1/3 border-b sm:border-b-0 sm:border-r border-border/50 relative">
                    <select
                      className="w-full bg-transparent appearance-none px-6 py-4 text-sm font-medium text-foreground focus:outline-none cursor-pointer"
                      value={selectedGrant?.id || ""}
                      onChange={(e) => {
                        const targetId = Number(e.target.value);
                        const g = grants.find(x => x.id === targetId);
                        if (g) setSelectedGrant(g);
                      }}
                    >
                      <option value="" disabled>Select Grant Program</option>
                      {grants.map(g => (
                        <option key={g.id} value={g.id}>{g.program_name}</option>
                      ))}
                    </select>
                    {/* Select arrow */}
                    <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-muted">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6" /></svg>
                    </div>
                  </div>

                  {/* Topic Input */}
                  <div className="flex-1 w-full relative">
                    <input
                      type="text"
                      className="w-full bg-transparent px-6 py-4 text-base text-foreground placeholder-muted/50 focus:outline-none"
                      placeholder="e.g. AI-driven drug discovery for tropical diseases..."
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleStartPipeline();
                      }}
                    />
                  </div>

                  {/* Submit Button */}
                  <div className="p-2 w-full sm:w-auto">
                    <button
                      onClick={handleStartPipeline}
                      disabled={!selectedGrant || !topic.trim()}
                      className="w-full sm:w-auto bg-foreground text-white rounded-2xl px-6 py-3 text-sm font-medium flex items-center justify-center gap-2 hover:bg-zinc-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Search className="w-4 h-4" />
                      Generate
                    </button>
                  </div>
                </div>
              </div>


              {/* Iteration Slider & Advanced settings below input */}
              <div className="mt-6 flex flex-col sm:flex-row items-center justify-between px-4 gap-4">
                <button
                  onClick={handleScrape}
                  disabled={isScraping}
                  className="text-xs font-medium text-muted hover:text-foreground transition-colors flex items-center gap-1.5 bg-surface/50 px-3 py-1.5 rounded-full border border-border"
                >
                  {isScraping ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <div className="w-1.5 h-1.5 rounded-full bg-brand-purple" />
                  )}
                  {isScraping ? "Scraping SERB..." : grants.length > 0 ? `${grants.length} Programs Loaded` : "Fetch Programs"}
                </button>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted font-medium">Iterations: {maxIterations}</span>
                  <input
                    type="range"
                    min={1}
                    max={5}
                    value={maxIterations}
                    onChange={(e) => setMaxIterations(Number(e.target.value))}
                    className="w-24 h-1bg-border rounded-full appearance-none cursor-pointer"
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Dashboard 3-Panel State */}
        <AnimatePresence>
          {hasStarted && (
            <motion.div
              initial={{ opacity: 0, y: 50, filter: "blur(10px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="w-full max-w-screen-2xl mx-auto flex h-full p-4 sm:p-6 gap-4 sm:gap-6 z-10"
            >
              {/* Left Panel - Replaced old solid sidebar with floating glass card */}
              <LeftPanel
                grants={grants}
                selectedGrant={selectedGrant}
                onSelectGrant={setSelectedGrant}
                topic={topic}
                onTopicChange={setTopic}
                maxIterations={maxIterations}
                onMaxIterationsChange={setMaxIterations}
                onScrape={handleScrape}
                onStart={handleStartPipeline}
                isScraping={isScraping}
                isLoading={isLoading}
              />

              {/* Main Workspace */}
              <MainWorkspace
                pipelineResult={pipelineResult}
                pipelineStatus={pipelineStatus}
                selectedIteration={selectedIteration}
                onSelectIteration={setSelectedIteration}
                isLoading={isLoading}
              />

              {/* Right Panel */}
              <RightPanel
                pipelineResult={pipelineResult}
                pipelineStatus={pipelineStatus}
                selectedIteration={selectedIteration}
                isLoading={isLoading}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Error Toast */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9, y: 10 }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 glass-panel-heavy bg-red-50/90 border border-red-200/50 rounded-2xl px-6 py-3 flex items-center gap-3 shadow-lg"
          >
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <span className="text-sm font-medium text-red-900">{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-2 text-red-700 hover:text-red-950 p-1"
            >
              ✕
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
