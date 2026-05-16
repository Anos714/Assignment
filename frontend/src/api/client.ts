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
const RAG_BASE_URL = import.meta.env.VITE_RAG_BASE_URL ?? "/rag";
const MAX_DOCUMENT_UPLOAD_BYTES = 25 * 1024 * 1024;

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

  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, {
      ...options,
      headers,
    });
  } catch (error) {
    throw new ApiError("API server is not reachable. Please start the backend service and try again.", 0, error);
  }

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

function parseResponsePayload(responseText: string) {
  if (!responseText) {
    return null;
  }
  try {
    return JSON.parse(responseText);
  } catch {
    return responseText;
  }
}

function uploadRequest<T>(path: string, file: File, onProgress?: (progress: number) => void): Promise<T> {
  const token = localStorage.getItem("access_token");
  const body = new FormData();
  body.append("file", file);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_BASE_URL}${path}`);

    if (token) {
      xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    }

    xhr.upload.addEventListener("progress", (event) => {
      if (!event.lengthComputable) {
        return;
      }
      onProgress?.(Math.min(99, Math.round((event.loaded / event.total) * 100)));
    });

    xhr.addEventListener("load", () => {
      const payload = parseResponsePayload(xhr.responseText);
      if (xhr.status < 200 || xhr.status >= 300) {
        reject(new ApiError(`Request failed with ${xhr.status}`, xhr.status, payload));
        return;
      }
      onProgress?.(100);
      resolve(payload as T);
    });

    xhr.addEventListener("error", () => {
      reject(new ApiError("API server is not reachable. Please start the backend service and try again.", 0, null));
    });

    xhr.addEventListener("abort", () => {
      reject(new ApiError("Upload was cancelled.", 0, null));
    });

    xhr.send(body);
  });
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
  uploadDocument: (file: File, onProgress?: (progress: number) => void) =>
    uploadRequest<KnowledgeDocument>("/documents/", file, onProgress),
  ragHealth: () => request<ServiceHealth>("/health", {}, RAG_BASE_URL),
};

export { MAX_DOCUMENT_UPLOAD_BYTES };
