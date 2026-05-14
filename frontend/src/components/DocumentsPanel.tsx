import type { ChangeEvent } from "react";
import type { KnowledgeDocument } from "../api";
import { DocumentRow } from "./DocumentRow";

type DocumentsPanelProps = {
  documents: KnowledgeDocument[];
  isDeleting?: boolean;
  isLoading?: boolean;
  isUploading?: boolean;
  selectedDocumentIds: string[];
  onDeleteDocument: (documentId: string) => void;
  onToggleDocument: (documentId: string) => void;
  onUploadDocument: (file: File) => void;
};

export function DocumentsPanel({
  documents,
  isDeleting,
  isLoading,
  isUploading,
  onDeleteDocument,
  selectedDocumentIds,
  onToggleDocument,
  onUploadDocument,
}: DocumentsPanelProps) {
  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) {
      onUploadDocument(file);
      event.target.value = "";
    }
  }

  return (
    <div className="panel documents-panel" id="documents">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Sources</p>
          <h2>Documents</h2>
        </div>
        <label className="upload-button">
          {isUploading ? "Uploading" : "Upload"}
          <input disabled={isUploading} onChange={handleFileChange} type="file" accept=".pdf,.docx,.txt" />
        </label>
      </div>

      <div className="drop-zone">
        <strong>Drop files here</strong>
        <span>PDF, DOCX, and TXT files move through ingestion before chat.</span>
      </div>

      <div className="document-list">
        {isLoading && <p className="muted-text">Loading documents...</p>}
        {!isLoading && documents.length === 0 && <p className="muted-text">No documents uploaded yet.</p>}
        {documents.map((document) => (
          <DocumentRow
            document={document}
            isSelected={selectedDocumentIds.includes(document.id)}
            isDeleting={isDeleting}
            key={document.id}
            onDelete={() => onDeleteDocument(document.id)}
            onToggle={() => onToggleDocument(document.id)}
          />
        ))}
      </div>
    </div>
  );
}
