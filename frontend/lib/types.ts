/** TypeScript interfaces matching backend schemas */

export interface Source {
  url: string;
  title?: string;
  credibility_score?: number;
  relevance_score?: number;
  content_preview?: string;
}

export interface ResearchSession {
  id: string;
  query: string;
  phase: string;
  plan?: Record<string, unknown>;
  findings?: unknown[];
  analysis?: Record<string, unknown>;
  report?: string;
  evaluation?: Record<string, unknown>;
  sources: Source[];
  total_tokens: number;
  total_cost: number;
  started_at?: string;
  completed_at?: string;
  revision_count: number;
  error?: string;
}

export interface WSMessage {
  type:
    | "agent.thought"
    | "agent.action"
    | "agent.result"
    | "research.phase_change"
    | "research.progress"
    | "research.complete"
    | "research.error"
    | "source.found"
    | "plan_created"
    | "phase.change"
    | "ping";
  data: Record<string, unknown>;
  timestamp: string;
  session_id: string;
}

export interface AgentThought {
  agent_name: string;
  thought_type: string;
  content: string;
  timestamp: number;
  tokens_used?: number;
  cost_usd?: number;
  metadata?: Record<string, unknown>;
}
