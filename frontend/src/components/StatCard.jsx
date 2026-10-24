
function StatCard({ title, value, note, icon, variant = 'purple' }) {
  return (
    <article className="stat-card">
      <div className="stat-top">
        <span>{title}</span>
        <span className={`stat-icon ${variant}`}>
          {icon}
        </span>
      </div>

      <h2>{value}</h2>

      {note && <p className="stat-note">{note}</p>}
    </article>
  )
}

export default StatCard
