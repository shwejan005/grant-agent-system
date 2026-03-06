import { Grant, PipelineStatus, PipelineResult } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}${url}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    if (!res.ok) {
        const error = await res.text();
        throw new Error(`API Error ${res.status}: ${error}`);
    }
    return res.json();
}

export async function fetchGrants(): Promise<{ grants: Grant[]; count: number }> {
    return fetchJSON("/api/grants");
}

export async function triggerScrape(): Promise<{
    message: string;
    count: number;
    programs: string[];
}> {
    return fetchJSON("/api/grants/scrape", { method: "POST" });
}

export async function getGrant(id: number): Promise<Grant> {
    return fetchJSON(`/api/grants/${id}`);
}

export async function startPipeline(params: {
    grant_id: number;
    topic: string;
    max_iterations?: number;
    score_threshold?: number;
}): Promise<{ message: string; run_id: number; status: string }> {
    return fetchJSON("/api/pipeline/start", {
        method: "POST",
        body: JSON.stringify(params),
    });
}

export async function getPipelineStatus(runId: number): Promise<PipelineStatus> {
    return fetchJSON(`/api/pipeline/status/${runId}`);
}

export async function getPipelineResults(runId: number): Promise<PipelineResult> {
    return fetchJSON(`/api/pipeline/results/${runId}`);
}

export async function listRuns(): Promise<{
    runs: { run_id: number; grant_program: string; research_topic: string; status: string }[];
    count: number;
}> {
    return fetchJSON("/api/pipeline/runs");
}
