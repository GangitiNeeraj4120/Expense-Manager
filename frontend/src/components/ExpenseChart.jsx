function ExpenseChart({ dailySpending = [] }) {
  const days = dailySpending.length ? dailySpending : []
  const maxAmount = Math.max(...days.map((item) => Number(item.amount) || 0), 1)
  const yMax = Math.ceil(maxAmount / 1000) * 1000 || 1000
  const labels = [yMax, yMax * 0.75, yMax * 0.5, yMax * 0.25, 0]

  return (
    <article className="panel chart-panel">
      <div className="panel-heading">
        <div><h3>Spending overview</h3><p>Daily totals from the last seven days</p></div>
        <span className="select-button">Last 7 days</span>
      </div>
      <div className="chart">
        <div className="chart-y-labels">
          {labels.map((value) => <span key={value}>{value >= 1000 ? `₹${(value / 1000).toFixed(value % 1000 ? 1 : 0)}k` : `₹${value}`}</span>)}
        </div>
        <div className="chart-plot">
          {days.map((item) => {
            const amount = Number(item.amount) || 0
            const height = Math.max(2, (amount / yMax) * 100)
            return (
              <div className="bar-column" key={item.date} title={`${item.day}: ₹${amount.toLocaleString('en-IN')}`}>
                <div className="bar" style={{ height: `${height}%` }} />
                <span>{item.day}</span>
              </div>
            )
          })}
          {!days.length && <p>No spending data available.</p>}
        </div>
      </div>
    </article>
  )
}

export default ExpenseChart
