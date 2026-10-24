
function ExpenseChart() {
  const barHeights = [35, 55, 42, 78, 50, 90, 62]
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

  return (
    <article className="panel chart-panel">
      <div className="panel-heading">
        <div>
          <h3>Spending overview</h3>
          <p>Your spending throughout this week</p>
        </div>

        <button className="select-button">This week⌄</button>
      </div>

      <div className="chart">
        <div className="chart-y-labels">
          <span>₹4k</span>
          <span>₹3k</span>
          <span>₹2k</span>
          <span>₹1k</span>
          <span>₹0</span>
        </div>

        <div className="chart-plot">
          {barHeights.map((height, index) => (
            <div className="bar-column" key={days[index]}>
              <div
                className={`bar ${index === 5 ? 'highlight' : ''}`}
                style={{ height: `${height}%` }}
              />
              <span>{days[index]}</span>
            </div>
          ))}
        </div>
      </div>
    </article>
  )
}

export default ExpenseChart
