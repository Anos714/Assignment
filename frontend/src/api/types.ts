export type DocumentStatus = "queued" | "processing" | "ready" | "failed";

export type User = {
  id: string;
  email: string;
  full_name: string;
  created_at?: string;
};

export type AuthTokens = {
  access: string;
  refresh: string;
};

export type AuthCredentials = {
  email: string;
  password: string;
};

export type SignupPayload = AuthCredentials & {
  full_name: string;
};

export type KnowledgeDocument = {
  id: string;
  filename: string;
  file_type?: string;
  status: DocumentStatus;
  chunk_count?: number;
  file_size?: number;
  error_message?: string;
  created_at: string;
  updated_at?: string;
};

export type DashboardStats = {
  documents_total: number;
  documents_ready: number;
  documents_processing: number;
  chat_sessions: number;
  questions_asked: number;
  cache_hit_rate: number;
};

export type Citation = {
  document_id: string;
  document_name: string;
  chunk_id: string;
  page_number?: number;
  score: number;
  supporting_text: string;
};

export type AskResponse = {
  message_id: string;
  status: "answered" | "insufficient_context";
  answer: string;
  citations: Citation[];
  retrieval: {
    top_k: number;
    threshold: number;
    cache_hit: boolean;
    best_score?: number;
  };
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  status?: "answered" | "insufficient_context";
  citations?: Citation[];
  created_at?: string;
};

export type ChatSession = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
};

export type PaginatedResponse<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
};

export type ServiceHealth = {
  status: string;
  service?: string;
};
