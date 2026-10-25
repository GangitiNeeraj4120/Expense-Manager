
import streamlit as st

st.set_page_config(
    page_title="Expense-Manager",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Expense-Manager")
st.subheader("Your money. Your habits. An AI that remembers.")

st.write(
    "Welcome to Expense-Manager — your AI-powered "
    "personal expense management assistant."
)

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric("Total Spending", "₹2,279")
col2.metric("Monthly Budget", "₹20,000")
col3.metric("Budget Remaining", "₹17,721")

st.divider()

st.subheader("Recent Transactions")

transactions = [
    {"Merchant": "Starbucks", "Amount (₹)": 250, "Category": "Social Spending"},
    {"Merchant": "Uber", "Amount (₹)": 180, "Category": "Transport"},
    {"Merchant": "Zudio", "Amount (₹)": 1200, "Category": "Shopping"},
    {"Merchant": "Netflix", "Amount (₹)": 649, "Category": "Entertainment"},
]

st.dataframe(
    transactions,
    width="stretch",
    hide_index=True
)

st.subheader("Spending Overview")

st.bar_chart(
    {
        "Amount (₹)": [250, 180, 1200, 649]
    }
)

st.caption("Demo mode: all figures are sample data.")
