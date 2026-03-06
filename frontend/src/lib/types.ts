export interface Grant {
    id: number;
    program_name: string;
    description: string;
    eligibility: string;
    evaluation_criteria: string;
    funding_limit: string;
    proposal_requirements: string;
    application_guidelines: string;
    deadlines: string;
    scraped_at: string;
}

export interface Proposal {
    iteration: number;
    title: string;
    abstract: string;
    background: string;
    objectives: string;
    methodology: string;
    expected_impact: string;
    deliverables: string;
    full_text?: string;
}

export interface BudgetItem {
    item: string;
    quantity: number;
    unit_cost: string;
    total_cost: string;
    justification: string;
}

export interface BudgetCategory {
    category: string;
    items: BudgetItem[];
    subtotal: string;
}

export interface Milestone {
    milestone: string;
    start_month: number;
    end_month: number;
    deliverables: string[];
    budget_allocation: string;
}

export interface Budget {
    iteration: number;
    budget_table: BudgetCategory[];
    milestone_schedule: Milestone[];
    cost_justification: string;
    total_budget?: string;
}

export interface ScoreDetail {
    score: number;
    max_score: number;
    feedback: string;
}

export interface Evaluation {
    iteration: number;
    total_score: number;
    rubric_breakdown: Record<string, ScoreDetail>;
    critique_report: string;
    missing_sections: string[];
    rule_scores: Record<string, ScoreDetail>;
    llm_scores: Record<string, ScoreDetail>;
    strengths?: string[];
    weaknesses?: string[];
    improvement_suggestions?: string[];
}

export interface Refinement {
    iteration: number;
    change_summary: {
        section: string;
        change: string;
        addresses: string;
    }[];
    sections_improved: string[];
}

export interface PipelineIteration {
    iteration: number;
    proposal: Proposal | null;
    budget: Budget | null;
    evaluation: Evaluation | null;
    refinement: Refinement | null;
}

export interface Guidelines {
    eligibility_rules: string[];
    evaluation_criteria: {
        criterion: string;
        weight_percent: number;
        description: string;
    }[];
    formatting_requirements: string[];
    funding_constraints: Record<string, unknown>;
    rubric_weights: Record<string, number>;
}

export interface PipelineResult {
    run_id: number;
    status: string;
    grant_program: string;
    research_topic: string;
    total_iterations: number;
    final_score: number;
    score_history: number[];
    guidelines: Guidelines | null;
    iterations: PipelineIteration[];
}

export interface PipelineStatus {
    run_id: number;
    status: string;
    stage: string;
    iteration: number;
    max_iterations: number;
    scores: number[];
    message: string;
    result?: PipelineResult;
}
