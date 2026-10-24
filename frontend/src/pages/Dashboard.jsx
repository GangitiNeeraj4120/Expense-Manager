import {
  ArrowUpRight,
  ArrowDownRight,
  Wallet,
  ShoppingBag,
  CircleDollarSign,
  Coffee,
  Car,
} from 'lucide-react'
import StatCard from '../components/StatCard'
import ExpenseTable from '../components/ExpenseTable'
import ExpenseChart from '../components/ExpenseChart'
const transactions = [
  { name: 'Starbucks', category: 'Food & Drinks', date: 'Oct 22, 2026', amount: -250, icon: Coffee },
  { name: 'Uber', category: 'Transport', date: 'Oct 21, 2026', amount: -180, icon: Car },
  { name: 'Zudio', category: 'Shopping', date: 'Oct 20, 2026', amount: -1200, icon: ShoppingBag },
  { name: 'Monthly allowance', category: 'Income', date: 'Oct 18, 2026', amount: 5000, icon: CircleDollarSign },
]

function Dashboard() {
  return (
    <div className="page-content">
      <section className="welcome-row">
        <div>
          <p className="eyebrow">SATURDAY, OCTOBER 24, 2026</p>
          <h1>Your financial overview</h1>
          <p className="subtitle">Here's what's happening with your money today.</p>
        </div>
        <button
          className="primary-button"
          onClick={() => alert('Transaction form will be added next!')}
        >
          + Add transaction
        </button>
      </section>

      <section className="stats-grid">
        <StatCard
        title="Total balance"
        value="₹23,540.00"
        note="↗ 8.2% vs last month"
        icon={<Wallet size={19} />}
        variant="purple"
        />
        <StatCard
        title="Monthly spending"
        value="₹8,240.00"
        note="↘ 3.1% vs last month"
        icon={<ShoppingBag size={19} />}
        variant="orange"
        />
        <StatCard
        title="Budget remaining"
        value="₹11,760.00"
        note="58.8% of budget left"
        icon={<CircleDollarSign size={19} />}
        variant="green"
        />
      </section>


       
  



      <section className="content-grid">
        <ExpenseChart />
        
         

        <article className="panel category-panel">
          <div className="panel-heading">
            <div>
              <h3>Spending by category</h3>
              <p>Where your money goes</p>
            </div>
            <button className="more-button">•••</button>
          </div>

          <div className="donut-wrap">
            <div className="donut">
              <div><strong>₹8,240</strong><span>Total spent</span></div>
            </div>
          </div>

          <div className="category-legend">
            <div><span><i className="dot purple-dot" /> Food & drinks</span><strong>35%</strong></div>
            <div><span><i className="dot orange-dot" /> Shopping</span><strong>28%</strong></div>
            <div><span><i className="dot blue-dot" /> Transport</span><strong>22%</strong></div>
            <div><span><i className="dot green-dot" /> Other</span><strong>15%</strong></div>
          </div>
        </article>
      </section>

      <section className="panel transactions-panel">
        <div className="panel-heading">
          <div>
            <h3>Recent transactions</h3>
            <p>Your latest financial activity</p>
          </div>
        </div>
        <ExpenseTable transactions={transactions} />
      </section>
      </div>
  )
}

export default Dashboard
