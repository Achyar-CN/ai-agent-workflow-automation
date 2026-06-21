/** Data contract — mirrors the backend Pydantic models in
 *  `backend/app/schemas.py`. Keep the two in sync. */

export type Verdict = "GO" | "NO_GO";

export interface ICP {
  target_industries: string[];
  company_sizes: string[];
  regions: string[];
  buying_signals: string[];
  value_proposition: string;
  sender_name: string;
  sender_company: string;
  sender_role: string;
}

export interface CompanyProfile {
  name: string;
  industry: string;
  size: string;
  location: string;
  description: string;
  products: string[];
  recent_signals: string[];
  website: string;
  sources: string[];
}

export interface KeyPerson {
  name: string;
  title: string;
  relevance: string;
  source_url: string;
  email_guess: string;
}

export interface Qualification {
  fit_score: number;
  verdict: Verdict;
  reasoning: string;
  matched_criteria: string[];
  gaps: string[];
}

export interface EmailDraft {
  recipient: string;
  subject: string;
  body: string;
  personalization_hooks: string[];
}

// ── Pipeline streaming ──────────────────────────────────────────────────────

export type Stage = "research" | "enrich" | "qualify" | "draft";
export type StageStatus = "start" | "done" | "skipped" | "error";

export interface StageEvent {
  stage: Stage;
  status: StageStatus;
  data?: Record<string, unknown> | null;
  message?: string;
}

export const STAGES: { id: Stage; label: string; hint: string }[] = [
  { id: "research", label: "Research", hint: "Profiling the company from public sources" },
  { id: "enrich", label: "Key People", hint: "Finding decision-makers" },
  { id: "qualify", label: "Qualify", hint: "Scoring fit against your ICP" },
  { id: "draft", label: "Draft Email", hint: "Writing a personalized cold email" },
];

/** Empty ICP for form initialization. */
export const EMPTY_ICP: ICP = {
  target_industries: [],
  company_sizes: [],
  regions: [],
  buying_signals: [],
  value_proposition: "",
  sender_name: "",
  sender_company: "",
  sender_role: "",
};
