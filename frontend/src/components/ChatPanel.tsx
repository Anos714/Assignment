import { FormEvent } from "react";
import type { ChatMessage } from "../api";
import { MessageBubble } from "./MessageBubble";

type ChatPanelProps = {
  activeChatId: string | null;
  isAsking?: boolean;
  isLoading?: boolean;
  messages: ChatMessage[];
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
        {isLoading && <p className="muted-text">Loading messages...</p>}
        {!isLoading && messages.length === 0 && (
          <p className="muted-text">Ask a question once your documents are ready.</p>
        )}
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isAsking && (
          <article className="message assistant-message">
            <div className="message-meta">
              <strong>Assistant</strong>
            </div>
            <p>Retrieving grounded context...</p>
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
