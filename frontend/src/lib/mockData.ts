import type { ChatMessage, KnowledgeDocument } from "../api";

export const documents: KnowledgeDocument[] = [
  {
    id: "doc-1",
    filename: "vendor-agreement.pdf",
    status: "ready",
    chunk_count: 42,
    file_size: 123456,
    created_at: "2026-05-12T07:15:00Z",
  },
  {
    id: "doc-2",
    filename: "onboarding-notes.docx",
    status: "processing",
    chunk_count: 16,
    created_at: "2026-05-12T08:30:00Z",
  },
  {
    id: "doc-3",
    filename: "pricing-policy.txt",
    status: "ready",
    chunk_count: 19,
    created_at: "2026-05-11T16:10:00Z",
  },
];

export const initialMessages: ChatMessage[] = [
  {
    id: "m-1",
    role: "user",
    content: "What are the termination conditions in the vendor agreement?",
  },
  {
    id: "m-2",
    role: "assistant",
    status: "answered",
    content:
      "The agreement allows termination with 30 days written notice. It also allows immediate termination if either party materially breaches the agreement.",
    citations: [
      {
        document_id: "doc-1",
        document_name: "vendor-agreement.pdf",
        chunk_id: "chunk-18",
        page_number: 4,
        score: 0.87,
        supporting_text:
          "Either party may terminate this Agreement upon thirty (30) days written notice. Immediate termination is permitted after a material breach.",
      },
    ],
  },
  {
    id: "m-3",
    role: "user",
    content: "Does it mention renewal pricing?",
  },
  {
    id: "m-4",
    role: "assistant",
    status: "insufficient_context",
    content:
      "I could not find enough supporting information in your uploaded documents to answer that question.",
    citations: [],
  },
];

export const suggestedQuestions = [
  "Summarize the uploaded policies",
  "What changed in the latest agreement?",
  "Where is customer data mentioned?",
];

export function createPreviewAnswer(): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role: "assistant",
    status: "answered",
    content:
      "This is ready to connect to the Django chat endpoint. The interface already reserves space for grounded answers, warnings, retrieval details, and source citations.",
    citations: [
      {
        document_id: "doc-1",
        document_name: "vendor-agreement.pdf",
        chunk_id: "chunk-preview",
        page_number: 2,
        score: 0.82,
        supporting_text:
          "The backend response can replace this preview message with citation-backed text from retrieved document chunks.",
      },
    ],
  };
}
