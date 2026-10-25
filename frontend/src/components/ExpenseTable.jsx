
import {
  ShoppingBag,
  Coffee,
  Car,
  Wallet,
  CircleDollarSign,
} from 'lucide-react'

const iconMap = {
  ShoppingBag,
  Coffee,
  Car,
  Wallet,
  CircleDollarSign,
}

function ExpenseTable({ transactions = [] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>TRANSACTION</th>
            <th>CATEGORY</th>
            <th>DATE</th>
            <th className="amount-cell">AMOUNT</th>
          </tr>
        </thead>

        <tbody>
          {transactions.map((tx, index) => {
            const Icon =
              typeof tx.icon === 'string'
                ? iconMap[tx.icon] || Wallet
                : tx.icon || Wallet

            return (
              <tr key={tx.id ?? tx.name ?? index}>
                <td>
                  <div className="transaction-name">
                    <span className="transaction-icon">
                      <Icon size={18} />
                    </span>
                    <strong>{tx.name}</strong>
                  </div>
                </td>

                <td>
                  <span className="category-pill">
                    {tx.category}
                  </span>
                </td>

                <td>{tx.date}</td>

                <td
                  className={`amount-cell ${
                    tx.amount > 0 ? 'income' : ''
                  }`}
                >
                  {tx.amount > 0 ? '+' : '−'}₹
                  {Math.abs(Number(tx.amount)).toLocaleString('en-IN')}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default ExpenseTable
