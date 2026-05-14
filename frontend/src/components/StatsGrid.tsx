import type { DashboardStats } from "../api";

export function StatsGrid({ stats }: { stats?: DashboardStats }) {
  return (
    <section className="stats-grid" aria-label="Workspace stats">
      <StatCard label="Documents" value={`${stats?.documents_total ?? 0}`} detail={`${stats?.documents_ready ?? 0} ready`} />
      <StatCard label="Processing" value={`${stats?.documents_processing ?? 0}`} detail="Ingestion jobs" />
      <StatCard
        label="Questions"
        value={`${stats?.questions_asked ?? 0}`}
        detail={`${Math.round((stats?.cache_hit_rate ?? 0) * 100)}% cache hit rate`}
      />
      <StatCard label="Chats" value={`${stats?.chat_sessions ?? 0}`} detail="Saved sessions" />
    </section>
  );
}

function StatCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <article className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}
