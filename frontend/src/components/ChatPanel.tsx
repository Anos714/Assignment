import { FormEvent } from "react";
import type { ChatMessage } from "../api";
import { MessageBubble } from "./MessageBubble";

type ChatPanelProps = {
  activeChatId: string | null;
  isAsking?: boolean;
  isLoading?: boolean;
  messages: ChatMessage[];
  pendingQuestion?: string;
  question: string;
  selectedCount: number;
  suggestedQuestions: string[];
  onQuestionChange: (question: string) => void;
  onAsk: (event: FormEvent<HTMLFormElement>) => void;
};

export function ChatPanel({
  activeChatId,
  isAsking,
  isLoading,
  messages,
  pendingQuestion,
  question,
  selectedCount,
  suggestedQuestions,
  onQuestionChange,
  onAsk,
}: ChatPanelProps) {
  return (
    <div className="chat-panel" id="chat">
      <div className="chat-intro">
        <p className="eyebrow">Grounded chat</p>
        <h2>Ask across selected sources.</h2>
        <span className="scope-pill">{selectedCount} ready sources selected</span>
      </div>

      <div className="suggestion-row" aria-label="Suggested questions">
        {suggestedQuestions.map((item) => (
          <button type="button" key={item} onClick={() => onQuestionChange(item)}>
            {item}
          </button>
        ))}
      </div>

      <div className="messages" aria-live="polite">
        {isLoading && <MessageSkeletonList />}
        {!isLoading && messages.length === 0 && !pendingQuestion && (
          <div className="empty-state">
            <strong>No messages yet</strong>
            <p>Ask a question once your documents are ready. Answers will stay grounded in selected sources.</p>
          </div>
        )}
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {pendingQuestion && (
          <article className="message user-message pending-message">
            <div className="message-meta">
              <strong>You</strong>
              <span className="scope-pill">Sending</span>
            </div>
            <p>{pendingQuestion}</p>
          </article>
        )}
        {isAsking && (
          <article className="message assistant-message typing-message">
            <div className="message-meta">
              <strong>Assistant</strong>
            </div>
            <div className="typing-row" aria-label="Assistant is thinking">
              <span />
              <span />
              <span />
              <p>Retrieving grounded context</p>
            </div>
          </article>
        )}
      </div>

      <form className="ask-box" onSubmit={onAsk}>
        <input
          aria-label="Ask a question"
          onChange={(event) => onQuestionChange(event.target.value)}
          placeholder="Ask something that should be in your documents"
          value={question}
        />
        <button disabled={isAsking || !activeChatId} type="submit">
          {isAsking ? "Asking" : "Ask"}
        </button>
      </form>
    </div>
  );
}

function MessageSkeletonList() {
  return (
    <>
      <article className="message assistant-message skeleton-message">
        <span className="skeleton-line short" />
        <span className="skeleton-line" />
        <span className="skeleton-line wide" />
      </article>
      <article className="message user-message skeleton-message">
        <span className="skeleton-line short" />
        <span className="skeleton-line wide" />
      </article>
    </>
  );
}
