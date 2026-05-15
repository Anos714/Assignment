type TopbarProps = {
  isRefreshing?: boolean;
  onRefresh: () => void;
};

export function Topbar({ isRefreshing, onRefresh }: TopbarProps) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Reading workspace</p>
        <h1>What are we reading today?</h1>
      </div>
      <button className="ghost-button health-button" disabled={isRefreshing} onClick={onRefresh} type="button">
        <span className={isRefreshing ? "refresh-icon spinning" : "refresh-icon"} aria-hidden="true">
          ↻
        </span>
        <span>{isRefreshing ? "Refreshing" : "Refresh"}</span>
      </button>
    </header>
  );
}
