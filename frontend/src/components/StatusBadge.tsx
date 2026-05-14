import type { DocumentStatus } from "../api";

export function StatusBadge({ status }: { status: DocumentStatus }) {
  return <span className={`status-badge ${status}`}>{status}</span>;
}
