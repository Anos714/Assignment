import type {
  AskResponse,
  AuthCredentials,
  AuthTokens,
  ChatSession,
  DashboardStats,
  KnowledgeDocument,
  PaginatedResponse,
  ServiceHealth,
  SignupPayload,
  User,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";
const RAG_BASE_URL = import.meta.env.VITE_RAG_BASE_URL ?? "http://127.0.0.1:8001";

export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

async function request<T>(path: string, options: RequestInit = {}, baseUrl = API_BASE_URL): Promise<T> {
  const token = localStorage.getItem("access_token");
  const headers = new Headers(options.headers);

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      payload = await response.text();
    }
    throw new ApiError(`Request failed with ${response.status}`, response.status, payload);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  signup: (payload: SignupPayload) =>
    request<User>("/auth/signup/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  login: (payload: AuthCredentials) =>
    request<AuthTokens>("/auth/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  me: () => request<User>("/auth/me/"),
  getStats: () => request<DashboardStats>("/dashboard/stats/"),
  listDocuments: () => request<PaginatedResponse<KnowledgeDocument>>("/documents/"),
  getDocument: (documentId: string) => request<KnowledgeDocument>(`/documents/${documentId}/`),
  deleteDocument: (documentId: string) =>
    request<void>(`/documents/${documentId}/`, {
      method: "DELETE",
    }),
  listChats: () => request<PaginatedResponse<ChatSession>>("/chats/"),
  getChat: (chatId: string) => request<ChatSession>(`/chats/${chatId}/`),
  createChat: (title: string) =>
    request<ChatSession>("/chats/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    }),
  askQuestion: (chatId: string, question: string, documentIds: string[]) =>
    request<AskResponse>(`/chats/${chatId}/messages/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, document_ids: documentIds }),
    }),
  uploadDocument: (file: File) => {
    const body = new FormData();
    body.append("file", file);

    return request<KnowledgeDocument>("/documents/", {
      method: "POST",
      body,
    });
  },
  ragHealth: () => request<ServiceHealth>("/health", {}, RAG_BASE_URL),
};
