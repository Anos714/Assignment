import type { ChatSession, User } from "../api";

type SidebarProps = {
  activeChatId: string | null;
  chats: ChatSession[];
  isCreatingChat?: boolean;
  user?: User;
  onCreateChat: () => void;
  onLogout: () => void;
  onSelectChat: (chatId: string) => void;
};

export function Sidebar({
  activeChatId,
  chats,
  isCreatingChat,
  onCreateChat,
  onLogout,
  onSelectChat,
  user,
}: SidebarProps) {
  const initials = user?.full_name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || "KB";

  return (
    <aside className="sidebar" aria-label="Workspace navigation">
      <div className="brand">
        <span className="brand-mark">V</span>
        <div>
          <p>Veridian RAG</p>
          <span>Document reading room</span>
        </div>
      </div>

      <button className="new-chat-button" disabled={isCreatingChat} onClick={onCreateChat} type="button">
        New chat
      </button>

      <section className="sidebar-section" aria-label="Chat history">
        <p>Recent chats</p>
        <div className="sidebar-chat-list">
          {chats.length === 0 && <span className="sidebar-empty">No chats yet</span>}
          {chats.map((chat) => (
            <button
              className={chat.id === activeChatId ? "active" : ""}
              key={chat.id}
              onClick={() => onSelectChat(chat.id)}
              type="button"
            >
              {chat.title}
            </button>
          ))}
        </div>
      </section>

      <div className="profile-card">
        <span className="avatar">{initials}</span>
        <div>
          <strong>{user?.full_name ?? "Workspace"}</strong>
          <span>{user?.email ?? "Local development"}</span>
        </div>
        <button className="logout-button" onClick={onLogout} type="button">
          Logout
        </button>
      </div>
    </aside>
  );
}
