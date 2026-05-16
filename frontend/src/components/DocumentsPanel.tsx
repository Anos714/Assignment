import type { ChangeEvent, DragEvent } from "react";
import { useRef, useState } from "react";
import type { KnowledgeDocument } from "../api";
import { MAX_DOCUMENT_UPLOAD_BYTES } from "../api/client";
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
  uploadProgress?: number;
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
  uploadProgress = 0,
}: DocumentsPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [documentPendingDelete, setDocumentPendingDelete] = useState<KnowledgeDocument | null>(null);
  const [uploadError, setUploadError] = useState("");

  function uploadFile(file?: File) {
    if (!file || isUploading) {
      return;
    }
    if (!isAcceptedFile(file)) {
      setUploadError("Please upload a PDF, DOCX, or TXT file.");
      return;
    }
    if (file.size > MAX_DOCUMENT_UPLOAD_BYTES) {
      setUploadError("File is too large. Upload a PDF, DOCX, or TXT file up to 25 MB.");
      return;
    }
    setUploadError("");
    onUploadDocument(file);
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    uploadFile(file);
    event.target.value = "";
  }

  function handleDragOver(event: DragEvent<HTMLButtonElement>) {
    event.preventDefault();
    if (!isUploading) {
      setIsDragging(true);
    }
  }

  function handleDragLeave(event: DragEvent<HTMLButtonElement>) {
    if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
      setIsDragging(false);
    }
  }

  function handleDrop(event: DragEvent<HTMLButtonElement>) {
    event.preventDefault();
    setIsDragging(false);
    uploadFile(event.dataTransfer.files[0]);
  }

  return (
    <div className="panel documents-panel" id="documents">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Sources</p>
          <h2>Documents</h2>
        </div>
        <button
          className="upload-button min-w-24"
          disabled={isUploading}
          onClick={() => fileInputRef.current?.click()}
          type="button"
        >
          {isUploading ? `${uploadProgress}%` : "Upload"}
        </button>
      </div>

      <input
        ref={fileInputRef}
        className="hidden"
        disabled={isUploading}
        onChange={handleFileChange}
        type="file"
        accept=".pdf,.docx,.txt"
      />

      <button
        aria-label="Upload a document"
        className={[
          "drop-zone group w-full text-left transition duration-150",
          "hover:-translate-y-0.5 hover:border-[var(--sage)] hover:bg-[#edf3ef]",
          isDragging ? "is-dragging border-[var(--sage)] bg-[#edf3ef]" : "",
        ].join(" ")}
        disabled={isUploading}
        onClick={() => fileInputRef.current?.click()}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        type="button"
      >
        <span className="drop-zone-icon" aria-hidden="true">
          ↑
        </span>
        <span className="grid gap-1">
          <strong>{isUploading ? "Uploading document..." : isDragging ? "Release to upload" : "Drop files here"}</strong>
          <span>Click this box or drag a PDF, DOCX, or TXT file up to 25 MB.</span>
        </span>
        {isUploading && (
          <span className="upload-progress" aria-label={`Upload ${uploadProgress}% complete`}>
            <span className="upload-progress-track">
              <span className="upload-progress-bar" style={{ width: `${uploadProgress}%` }} />
            </span>
            <span className="upload-progress-label">{uploadProgress}%</span>
          </span>
        )}
      </button>
      {uploadError && <p className="form-error mt-3">{uploadError}</p>}

      <div className="document-list">
        {isLoading && <DocumentSkeletonList />}
        {!isLoading && documents.length === 0 && (
          <div className="empty-state compact">
            <strong>No documents uploaded yet</strong>
            <p>Add a PDF, DOCX, or TXT file to start asking grounded questions.</p>
          </div>
        )}
        {documents.map((document) => (
          <DocumentRow
            document={document}
            isSelected={selectedDocumentIds.includes(document.id)}
            isDeleting={isDeleting}
            key={document.id}
            onDelete={() => setDocumentPendingDelete(document)}
            onToggle={() => onToggleDocument(document.id)}
          />
        ))}
      </div>

      {documentPendingDelete && (
        <div className="modal-backdrop" role="presentation">
          <section
            aria-labelledby="delete-document-title"
            aria-modal="true"
            className="modal-panel"
            role="dialog"
          >
            <div>
              <p className="eyebrow">Delete source</p>
              <h2 id="delete-document-title">Remove this document?</h2>
              <p>
                This will delete <strong>{documentPendingDelete.filename}</strong> from your workspace. Existing answers
                may still appear in chat history, but the file will no longer be available as a source.
              </p>
            </div>
            <div className="modal-actions">
              <button
                className="ghost-button"
                disabled={isDeleting}
                onClick={() => setDocumentPendingDelete(null)}
                type="button"
              >
                Cancel
              </button>
              <button
                className="danger-button"
                disabled={isDeleting}
                onClick={() => {
                  onDeleteDocument(documentPendingDelete.id);
                  setDocumentPendingDelete(null);
                }}
                type="button"
              >
                {isDeleting ? "Deleting..." : "Delete document"}
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

function isAcceptedFile(file: File) {
  const filename = file.name.toLowerCase();
  return filename.endsWith(".pdf") || filename.endsWith(".docx") || filename.endsWith(".txt");
}

function DocumentSkeletonList() {
  return (
    <>
      <article className="document-row skeleton-message">
        <span className="skeleton-dot" />
        <span className="skeleton-line wide" />
        <span className="skeleton-line short" />
      </article>
      <article className="document-row skeleton-message">
        <span className="skeleton-dot" />
        <span className="skeleton-line wide" />
        <span className="skeleton-line short" />
      </article>
      <article className="document-row skeleton-message">
        <span className="skeleton-dot" />
        <span className="skeleton-line wide" />
        <span className="skeleton-line short" />
      </article>
    </>
  );
}
