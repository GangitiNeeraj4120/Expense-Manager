# Expense-Manager

**A smarter way to understand personal spending.**

Expense-Manager is a personal-finance project built around the idea that
tracking transactions is only the beginning. It aims to help users
understand where their money goes through a visual dashboard, structured
transaction data, and a conversational AI assistant that can use
financial records and saved spending context.

The project was developed by **Agentic Hackers (Team ID: 732559)** for
**MongoDB Track 1**. The project was initially discussed as
*SpendSense*; the GitHub repository and application name is
**Expense-Manager**.

> **Project status:** Work in progress. The React frontend and Python
> agent/database backend are present in the repository, but they are
> **not integrated end-to-end yet**. Several frontend screens still use
> local demo data, and the current backend snapshot does not include the
> FastAPI application entry point/API routes described in the planned
> architecture.

## Table of contents

-   [Why Expense-Manager?](#why-expense-manager)
-   [Core modules](#core-modules)
-   [How it works](#how-it-works)
-   [Technology stack](#technology-stack)
-   [Repository structure](#repository-structure)
-   [Current implementation status](#current-implementation-status)
-   [Getting started](#getting-started)
-   [Configuration](#configuration)
-   [Demo data](#demo-data)
-   [Roadmap](#roadmap)
-   [Team](#team)

## Why Expense-Manager?

Financial records can be hard to interpret when they are just long lists
of transactions. Expense-Manager brings together:

-   **Transaction management** --- store and retrieve expenses with
    merchant, amount, category, date, and optional context.
-   **Spending analytics** --- calculate total spending and
    category-wise totals, and inspect trends over time.
-   **Conversational assistance** --- ask questions about spending,
    goals, and financial habits in natural language.
-   **Persistent financial memory** --- retain supported observations
    about spending patterns so future answers can be more context-aware.
-   **Memory comparison** --- explore the intended difference between
    generic answers and answers informed by stored context.

The goal is to move from *"What did I spend?"* towards *"What does my
spending history tell me, and what could I do next?"*

## Core modules

### 1. Dashboard

The dashboard is designed to make financial information easier to scan,
with summary cards, transaction records, and spending visualisations.

**Current state:** The React dashboard is a UI prototype and currently
displays hard-coded sample figures and transactions. It is not yet
reading from MongoDB.

### 2. AI Assistant

The intended assistant lets users ask questions about their
transactions, category totals, spending trends, recurring payments,
unusual transactions, budgets, and goals.

The backend includes a LangGraph workflow and financial tools that allow
the language model to request supported operations rather than inventing
financial figures.

**Current state:** The React chat uses demo responses. The separate
Python agent has a terminal entry point, but it is not connected to the
frontend through an API yet.

### 3. Memory Lab

The Memory Lab is intended to make saved financial context visible and
understandable. The backend represents memories using fields such as
type, condition, value, source, confidence, and status. Financial
analysis can create or update observations such as the largest spending
category over the last 30 days.

**Current state:** The React Memory Lab supports adding, searching, and
deleting sample memories in page state only. Those UI actions do not
currently persist to MongoDB or affect the agent.

### 4. Financial pattern analysis

Backend utilities can analyse:

-   Spending changes between recent and preceding 30-day periods.
-   Merchants with transactions at approximately monthly intervals.
-   Potentially unusual transactions relative to a category's historical
    amounts.
-   Average daily spending on weekdays versus weekends.
-   Recent spending against active spending-limit goals.

These are indicators for exploration, not proof of a subscription,
fraud, or an unnecessary purchase.

## How it works

The intended full application flow is:

1.  A user interacts with the dashboard or AI Assistant.
2.  The frontend sends a request to a backend API.
3.  The backend validates the request and retrieves the relevant
    financial records from MongoDB.
4.  For conversational queries, the LangGraph workflow prepares the
    message, refreshes financial analysis when due, retrieves active
    memories, and calls the language model.
5.  If needed, the model invokes a financial tool to query records or
    perform a supported operation.
6.  The backend returns a result for the frontend to display.

The backend agent workflow currently follows this general sequence:

`Prepare message → Refresh financial analysis → Retrieve memories → Call LLM ↔ Financial tools → Generate answer`

The tool loop allows the model to request data-backed operations before
producing a final response. Financial calculations are handled by
Python/MongoDB aggregation utilities; the language model interprets the
question and explains the returned results.

**Important distinction:** This describes the intended end-to-end
architecture. In the current repository snapshot, the React UI and
backend are still separate, and there is no FastAPI route layer
connecting them.

## Technology stack

  -----------------------------------------------------------------------
  Layer                   Technology              Role
  ----------------------- ----------------------- -----------------------
  Frontend                React, JavaScript, CSS  Dashboard and
                                                  interactive application
                                                  screens

  Frontend tooling        Vite                    Local development
                                                  server and production
                                                  build

  Icons                   Lucide React            Interface icons

  Backend language        Python                  Data access,
                                                  calculations, and agent
                                                  logic

  Database                MongoDB Atlas / PyMongo Transaction, goal,
                                                  memory, and
                                                  analysis-state storage

  Agent orchestration     LangGraph               Workflow, tool routing,
                                                  and agent state

  LLM integration         LangChain Groq          Language-model
                          integration             responses and tool
                                                  calling

  Configuration           `python-dotenv`         Load local environment
                                                  variables
  -----------------------------------------------------------------------

The planned architecture also includes a FastAPI API layer and HTTP
communication between the frontend and backend. That integration is not
present in this snapshot yet.

## Repository structure

``` text
Expense-Manager/
├── app.py                         # Small Streamlit demo dashboard
├── requirements.txt               # Python dependencies
├── backend/
│   ├── Agent/
│   │   ├── agent.py                # Terminal entry point for the agent
│   │   ├── graph.py                # LangGraph workflow
│   │   ├── state.py                # Shared agent state
│   │   ├── database_tools.py       # Financial tools exposed to the LLM
│   │   ├── memory_engine.py        # Memory retrieval and upsert logic
│   │   ├── financial_Analysis.py   # Periodic financial analysis
│   │   ├── pattern_analysis.py     # Trend and behaviour analysis
│   │   └── analysis_state.py       # Analysis freshness checks
│   └── database/
│       ├── database.py             # MongoDB connection and CRUD operations
│       ├── finance.py              # Spending and budget calculations
│       └── seed_data.py            # Demo-data seeding script (may need import-path fixes)
└── frontend/
    ├── package.json
    ├── index.html
    └── src/
        ├── App.jsx
        ├── pages/
        │   ├── Dashboard.jsx
        │   ├── AIAssistant.jsx
        │   ├── MemoryLab.jsx
        │   └── MemoryChallenge.jsx
        └── components/
            ├── ExpenseChart.jsx
            ├── ExpenseTable.jsx
            └── StatCard.jsx
```

## Current implementation status

  -----------------------------------------------------------------------
  Area                                Status in this repository snapshot
  ----------------------------------- -----------------------------------
  React application shell and         Present
  navigation                          

  Dashboard UI and visual components  Present; uses sample values

  AI Assistant UI                     Present; responses are demo text

  Memory Lab UI                       Present; memories are local page
                                      state

  MongoDB connection and indexes      Implemented in backend database
                                      module

  Transaction CRUD helpers            Implemented in backend database
                                      module

  Goals and budget calculation        Initial implementation present
  helpers                             

  Deterministic spending calculations Implemented in Python

  LangGraph agent and financial tools Implemented as a separate backend
                                      workflow

  Financial pattern analysis          Utility functions implemented

  Persistent memory retrieval and     Backend functions present
  upsert                              

  FastAPI API routes                  Not included in this snapshot

  Frontend-to-backend integration     Pending

  Authentication / multi-user         Not implemented end-to-end
  isolation                           

  Automated test coverage             Limited; includes
                                      analysis-freshness tests
  -----------------------------------------------------------------------

This table reflects the supplied code snapshot, not a claim that every
component has been fully tested in a deployed environment.

## Getting started

### Prerequisites

-   Node.js and npm
-   Python 3.11 or a compatible Python version
-   A MongoDB Atlas cluster or another reachable MongoDB deployment
-   A Groq API key for the LangGraph agent

### 1. Clone the repository

``` bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Expense-Manager
```

Replace the placeholder with the repository's actual GitHub URL.

### 2. Run the frontend prototype

``` bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in your terminal.

To create a production build:

``` bash
npm run build
```

The frontend currently runs independently and uses hard-coded/local demo
data; starting it does not connect it to the Python backend.

### 3. Configure the Python backend

From the repository root, create a local `.env` file:

``` dotenv
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-host>/
MONGODB_DATABASE=spendsense
GROQ_API_KEY=<your_groq_api_key>
```

-   `MONGODB_URI` is required by the database module.
-   `MONGODB_DATABASE` is optional; it defaults to `spendsense`.
-   `GROQ_API_KEY` is required to build the LLM-powered agent.

Use your own credentials. Do not commit `.env` or paste database/API
secrets into issues or public messages.

Create and activate a virtual environment from the repository root:

**Windows (PowerShell)**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:

``` bash
pip install -r requirements.txt
```

If pip reports a text-encoding error while reading `requirements.txt`,
re-save that file as UTF-8 and retry. The supplied archive contains it
in UTF-16 encoding.

### 4. Run the backend agent in the terminal

From the repository root, activate the virtual environment and run:

``` bash
cd backend
python -m Agent.agent
```

Enter a user ID when prompted, then type questions in the terminal. Type
`exit` or `quit` to stop the session.

This runs the standalone agent workflow; it does **not** start a web API
or connect the React frontend. MongoDB and Groq credentials must be
configured first.

## Database overview

The backend currently uses these MongoDB collections:

  -----------------------------------------------------------------------
  Collection                          Purpose
  ----------------------------------- -----------------------------------
  `transactions`                      Expense records, including amount,
                                      merchant, category, date, context,
                                      and optional memory references

  `goals`                             Spending-limit and savings-target
                                      records

  `memories`                          Active or inactive financial
                                      observations and user-related
                                      context

  `analysis_state`                    Tracks when a user's periodic
                                      financial analysis last succeeded
                                      and the status of the latest
                                      attempt
  -----------------------------------------------------------------------

The database module creates indexes for transaction dates/categories,
memory type/status, goal periods, and analysis state by user ID.

### Design principle: records vs. memories

Transactions and goals are the structured financial records used for
calculations. Memories are supporting context and observations, not a
replacement for the underlying records. For example, a saved observation
that shopping is a major spending category should not override a fresh
calculation from the transaction collection.

The current memory engine retrieves active memories from MongoDB and can
insert or update a memory with the same type and condition.
Semantic/vector retrieval and a complete user-isolated memory lifecycle
should not be assumed to be fully integrated in this snapshot.

## Demo data

The repository includes a `backend/database/seed_data.py` script
intended to populate a small October 2026 dataset for demonstrations,
including transactions, a spending limit, a savings target, and a sample
memory.

The script documents an expected transaction total of **₹2,000**:

  Category            Sample total
  ----------------- --------------
  Shopping                  ₹1,200
  Social Spending             ₹550
  Food & Dining               ₹150
  Transport                   ₹100
  **Total**             **₹2,000**

Review the script's imports and run it only against a development
database: it deletes documents tagged with its own `demo_batch` before
inserting the demo batch. The seed script's current import paths may
need adjustment before it runs successfully.

## Roadmap

Planned next steps include:

-   [ ] Add a FastAPI application and API routes for transactions,
    dashboard summaries, goals, the assistant, and memory operations.
-   [ ] Connect the React frontend to the backend API and replace demo
    values with database-backed data.
-   [ ] Connect the AI Assistant UI to the LangGraph agent.
-   [ ] Connect Memory Lab to persistent backend memory operations,
    including clear memory-on/memory-off comparison behaviour.
-   [ ] Improve memory retrieval, relevance filtering, user isolation,
    and memory lifecycle management.
-   [ ] Add validation, error handling, and broader automated tests.
-   [ ] Add authentication and stronger privacy/security controls.
-   [ ] Explore authorised transaction imports, spending alerts,
    predictive budgeting, recurring-payment detection, and goal-aware
    recommendations.

## Team

**Agentic Hackers --- Team ID: 732559**

Built for **MongoDB Track 1**.

------------------------------------------------------------------------

*Expense-Manager is a prototype for learning and demonstration. It is
not a bank-connected financial service and should not be treated as
professional financial advice. Use synthetic or non-sensitive data while
developing, and keep credentials out of version control.*
