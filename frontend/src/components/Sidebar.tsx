import type { ChatSession, DashboardStats, User } from "../api";

type SidebarProps = {
  activeChatId: string | null;
  chats: ChatSession[];
  isCollapsed?: boolean;
  isCreatingChat?: boolean;
  stats?: DashboardStats;
  statsLoading?: boolean;
  user?: User;
  onCreateChat: () => void;
  onLogout: () => void;
  onSelectChat: (chatId: string) => void;
  onToggleCollapse: () => void;
};

export function Sidebar({
  activeChatId,
  chats,
  isCollapsed,
  isCreatingChat,
  onCreateChat,
  onLogout,
  onSelectChat,
  onToggleCollapse,
  stats,
  statsLoading,
  user,
}: SidebarProps) {
  const initials = user?.full_name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || "KB";

  return (
    <aside
      className={[
        "sidebar",
        "transition-[padding] duration-200",
        isCollapsed ? "collapsed" : "",
      ].join(" ")}
      aria-label="Workspace navigation"
    >
      <div className="sidebar-topline">
        <div className="brand min-w-0">
          <span className="brand-mark">D</span>
          <div className="min-w-0">
            <p>DocuMind AI</p>
            <span>Document intelligence</span>
          </div>
        </div>
        <button
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="sidebar-collapse-button"
          onClick={onToggleCollapse}
          title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          type="button"
        >
          {isCollapsed ? "›" : "‹"}
        </button>
      </div>

      <button
        className="new-chat-button min-h-11"
        disabled={isCreatingChat}
        onClick={onCreateChat}
        title="New chat"
        type="button"
      >
        <span>{isCreatingChat ? "Creating..." : "New chat"}</span>
      </button>

      <section className="sidebar-section" aria-label="Dashboard overview">
        <p>Dashboard</p>
        {statsLoading ? (
          <div className="sidebar-stats-grid">
            <span className="skeleton-block" />
            <span className="skeleton-block" />
            <span className="skeleton-block" />
            <span className="skeleton-block" />
          </div>
        ) : (
          <div className="sidebar-stats-grid">
            <SidebarStat label="Files" value={stats?.documents_total ?? 0} />
            <SidebarStat label="Ready" value={stats?.documents_ready ?? 0} />
            <SidebarStat label="Asked" value={stats?.questions_asked ?? 0} />
            <SidebarStat label="Chats" value={stats?.chat_sessions ?? 0} />
          </div>
        )}
      </section>

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

      <div className="profile-card min-w-0">
        <span className="avatar" title={user?.full_name ?? "Workspace"}>
          {initials}
        </span>
        <div className="min-w-0">
          <strong>{user?.full_name ?? "Workspace"}</strong>
          <span>{user?.email ?? "Local development"}</span>
        </div>
        <button className="logout-button shrink-0" onClick={onLogout} type="button">
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}

function SidebarStat({ label, value }: { label: string; value: number }) {
  return (
    <article className="sidebar-stat">
      <strong>{value}</strong>
      <span>{label}</span>
    </article>
  );
}
