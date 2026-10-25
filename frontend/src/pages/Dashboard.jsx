import { useEffect, useState } from 'react'
import { Wallet, ShoppingBag, CircleDollarSign } from 'lucide-react'
import StatCard from '../components/StatCard'
import ExpenseTable from '../components/ExpenseTable'
import ExpenseChart from '../components/ExpenseChart'
import { getDashboardData } from '../services/api'

const money = (value) => value == null
  ? 'Not configured'
  : `₹${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`


function Dashboard() {
  const [dashboard, setDashboard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getDashboardData()
      .then(setDashboard)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const categories = dashboard?.category_totals || []
  const transactions = dashboard?.transactions || []
  const monthlySpending = dashboard?.monthly_spending ?? 0
  const budgetTarget = dashboard?.budget_target
  const budgetRemaining = dashboard?.budget_remaining
  const budgetUsed = budgetTarget > 0
    ? Math.min(100, Math.max(0, (monthlySpending / budgetTarget) * 100))
    : null
  const chartColors = ['#7967ec', '#f5a15f', '#65a9e9', '#50c7a1', '#d3a4e8']
  let donutCursor = 0
  const donutStops = categories.map((item, index) => {
    const start = donutCursor
    donutCursor += Number(item.percentage || 0)
    return `${chartColors[index % chartColors.length]} ${start}% ${donutCursor}%`
  })
  const donutBackground = donutStops.length ? `conic-gradient(${donutStops.join(', ')})` : '#eeeaf7'

  if (loading) return <div className="page-content"><p>Loading financial data from the database...</p></div>
  if (error) return <div className="page-content"><h1>Unable to load dashboard</h1><p>{error}</p><p>Check that the backend is running and MongoDB is connected.</p></div>

  return (
    <div className="page-content">
      <section className="welcome-row">
        <div>
          <p className="eyebrow">{new Date().toLocaleDateString('en-IN', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }).toUpperCase()}</p>
          <h1>Your financial overview</h1>
          <p className="subtitle">These figures are loaded from your database.</p>
        </div>
      </section>

      <section className="stats-grid">
        <StatCard title="Total balance" value={money(dashboard?.total_balance)} note="Balance tracking is not configured" icon={<Wallet size={19} />} variant="purple" />
        <StatCard title="Monthly spending" value={money(monthlySpending)} note="Current month · database total" icon={<ShoppingBag size={19} />} variant="orange" />
        <StatCard title="Budget remaining" value={money(budgetRemaining)} note={budgetUsed == null ? 'Add a spending-limit goal to track budget' : `${budgetUsed.toFixed(1)}% of budget used`} icon={<CircleDollarSign size={19} />} variant="green" />
      </section>

      <section className="content-grid">
        <ExpenseChart dailySpending={dashboard?.daily_spending || []} />

        <article className="panel category-panel">
          <div className="panel-heading">
            <div><h3>Spending by category</h3><p>Current month · database totals</p></div>
          </div>
          <div className="donut-wrap">
            <div className="donut" style={{ background: donutBackground }}>
              <div><strong>{money(monthlySpending)}</strong><span>Total spent</span></div>
            </div>
          </div>
          <div className="category-legend">
            {categories.length ? categories.slice(0, 5).map((item) => (
              <div key={item.category}>
                <span><i className="dot purple-dot" /> {item.category}</span>
                <strong>{Number(item.percentage || 0).toFixed(1)}% · {money(item.amount)}</strong>
              </div>
            )) : <p>No category spending found for this month.</p>}
          </div>
        </article>
      </section>

      <section className="panel transactions-panel">
        <div className="panel-heading"><div><h3>Recent transactions</h3><p>Your latest financial activity from MongoDB</p></div></div>
        {transactions.length ? <ExpenseTable transactions={transactions} /> : <p>No transactions found for this month.</p>}
      </section>
    </div>
  )
}

export default Dashboard
