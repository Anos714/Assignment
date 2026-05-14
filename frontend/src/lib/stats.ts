import type { KnowledgeDocument } from "../api";

export function countReadyDocuments(documents: KnowledgeDocument[]) {
  return documents.filter((document) => document.status === "ready").length;
}

export function countProcessingDocuments(documents: KnowledgeDocument[]) {
  return documents.filter((document) => ["processing", "queued"].includes(document.status)).length;
}
