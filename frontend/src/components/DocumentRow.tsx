import type { KnowledgeDocument } from "../api";
import { StatusBadge } from "./StatusBadge";

type DocumentRowProps = {
  document: KnowledgeDocument;
  isSelected: boolean;
  isDeleting?: boolean;
  onToggle: () => void;
  onDelete: () => void;
};

export function DocumentRow({ document, isDeleting, isSelected, onDelete, onToggle }: DocumentRowProps) {
  return (
    <article className="document-row">
      <label className="document-check">
        <input checked={isSelected} disabled={document.status !== "ready"} onChange={onToggle} type="checkbox" />
        <span>
          <strong>{document.filename}</strong>
          <small>
            {document.chunk_count ?? 0} chunks
            {document.file_size ? ` · ${formatFileSize(document.file_size)}` : ""}
          </small>
        </span>
      </label>
      <div className="document-actions">
        <StatusBadge status={document.status} />
        <button disabled={isDeleting} onClick={onDelete} type="button">
          Delete
        </button>
      </div>
    </article>
  );
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${Math.round(bytes / 1024)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
