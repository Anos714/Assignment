import type { ChatMessage } from "../api";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <article className={isUser ? "message user-message" : "message assistant-message"}>
      <div className="message-meta">
        <strong>{isUser ? "You" : "Assistant"}</strong>
        {message.status === "insufficient_context" && <span className="warning-tag">Needs more context</span>}
      </div>
      <p>{message.content}</p>

      {message.citations && message.citations.length > 0 && (
        <div className="citations">
          {message.citations.map((citation) => (
            <article className="citation-card" key={citation.chunk_id}>
              <div>
                <strong>{citation.document_name}</strong>
                <span>
                  Page {citation.page_number ?? "n/a"} - score {Math.round(citation.score * 100)}%
                </span>
              </div>
              <p>{citation.supporting_text}</p>
            </article>
          ))}
        </div>
      )}
    </article>
  );
}
