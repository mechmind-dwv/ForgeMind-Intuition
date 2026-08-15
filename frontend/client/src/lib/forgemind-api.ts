export type ProjectNode = {
  kind?: string;
  name: string;
  arg?: unknown;
};

export type CandidateInput = {
  id?: string;
  candidate_id?: string;
  description?: string;
  program: ProjectNode[];
  source?: string;
  metadata?: Record<string, unknown>;
};

/** Public ProjectInput contract accepted by the ForgeMind engine API. */
export type ProjectInput = {
  schema_version: "1.0";
  name: string;
  candidates: CandidateInput[];
  probes?: number[][];
  targets?: unknown[];
  metadata?: Record<string, unknown>;
  knowledge?: Array<Record<string, unknown>>;
};

export type IntuitionScore = {
  total: number;
  novelty: number;
  structural_similarity: number;
  compression: number;
  falsification_value: number;
  compositional_value: number;
  complexity_penalty: number;
  historical_failure: number;
  reasons: string[];
};

export type CandidateAdvice = {
  candidate_index: number;
  intuition: IntuitionScore;
  calibrated_score: number;
  experimental_value: number;
  recommendation: string;
};

export type EvaluateResponse = {
  project: string;
  candidate_count: number;
  results: CandidateAdvice[];
  engine: string;
};

export type EngineHealth = {
  status: string;
  engine: string;
  version: string;
};

const API_BASE = (import.meta.env.VITE_FORGEMIND_API_URL || "/api/engine").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers || {}) },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof payload?.detail === "string" ? payload.detail : `ForgeMind API error (${response.status})`;
    throw new Error(detail);
  }
  return payload as T;
}

export function getEngineHealth() {
  return request<EngineHealth>("/health");
}

export function evaluateProject(project: ProjectInput) {
  return request<EvaluateResponse>("/v1/evaluate", {
    method: "POST",
    body: JSON.stringify({ project }),
  });
}
