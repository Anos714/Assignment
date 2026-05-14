type TopbarProps = {
  onRefresh: () => void;
};

export function Topbar({ onRefresh }: TopbarProps) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Reading workspace</p>
        <h1>What are we reading today?</h1>
      </div>
      <button className="ghost-button health-button" onClick={onRefresh} type="button">
        Refresh
      </button>
    </header>
  );
}
