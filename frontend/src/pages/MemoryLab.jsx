import { useState } from 'react'
import {
  Brain,
  Plus,
  Search,
  Trash2,
  Lightbulb,
  ShieldCheck,
  Clock3,
  Tag,
} from 'lucide-react'

const initialMemories = [
  {
    id: 1,
    title: 'Monthly budget preference',
    detail: 'The user prefers to keep monthly spending within a fixed budget.',
    category: 'Budget',
    date: 'Saved for demo',
  },
  {
    id: 2,
    title: 'Expense tracking preference',
    detail: 'The user wants spending grouped into clear categories.',
    category: 'Preferences',
    date: 'Saved for demo',
  },
  {
    id: 3,
    title: 'Saving goal',
    detail: 'The user is interested in identifying opportunities to save money.',
    category: 'Goals',
    date: 'Saved for demo',
  },
]

function MemoryLab() {
  const [memories, setMemories] = useState(initialMemories)
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState('')
  const [detail, setDetail] = useState('')
  const [category, setCategory] = useState('Preferences')

  const filteredMemories = memories.filter((memory) =>
    `${memory.title} ${memory.detail} ${memory.category}`
      .toLowerCase()
      .includes(search.toLowerCase())
  )

  function addMemory(event) {
    event.preventDefault()
    if (!title.trim() || !detail.trim()) return

    setMemories((previous) => [
      {
        id: Date.now(),
        title: title.trim(),
        detail: detail.trim(),
        category,
        date: 'Added just now',
      },
      ...previous,
    ])

    setTitle('')
    setDetail('')
    setCategory('Preferences')
    setShowForm(false)
  }

  function deleteMemory(id) {
    setMemories((previous) => previous.filter((memory) => memory.id !== id))
  }

  return (
    <div className="page-content memory-page">
      <section className="welcome-row">
        <div>
          <p className="eyebrow">PERSONALISED AI MEMORY</p>
          <h1>Memory Lab</h1>
          <p className="subtitle">
            Explore the information an AI assistant could remember to personalise future conversations.
          </p>
        </div>

        <button className="primary-button" onClick={() => setShowForm(!showForm)}>
          <Plus size={16} style={{ verticalAlign: 'middle', marginRight: 5 }} />
          Add memory
        </button>
      </section>

      <section className="memory-info-grid">
        <article className="panel memory-info-card">
          <div className="memory-info-icon"><Brain size={21} /></div>
          <h3>{memories.length}</h3>
          <p>Demo memories</p>
        </article>
        <article className="panel memory-info-card">
          <div className="memory-info-icon green"><ShieldCheck size={21} /></div>
          <h3>Visible</h3>
          <p>Reviewable by the user</p>
        </article>
        <article className="panel memory-info-card">
          <div className="memory-info-icon orange"><Clock3 size={21} /></div>
          <h3>Session only</h3>
          <p>Not stored in a database</p>
        </article>
      </section>

      {showForm && (
        <form className="panel memory-form" onSubmit={addMemory}>
          <h3>Create a memory</h3>
          <label>
            Memory title
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="e.g. Preferred monthly budget"
              required
            />
          </label>
          <label>
            Memory details
            <textarea
              value={detail}
              onChange={(event) => setDetail(event.target.value)}
              placeholder="What should the assistant remember?"
              rows={3}
              required
            />
          </label>
          <label>
            Category
            <select value={category} onChange={(event) => setCategory(event.target.value)}>
              <option>Preferences</option>
              <option>Budget</option>
              <option>Goals</option>
              <option>Spending habits</option>
            </select>
          </label>
          <div className="memory-form-actions">
            <button type="button" className="chat-reset" onClick={() => setShowForm(false)}>
              Cancel
            </button>
            <button type="submit" className="primary-button">Save memory</button>
          </div>
        </form>
      )}

      <section className="panel memories-panel">
        <div className="panel-heading">
          <div>
            <h3>Remembered information</h3>
            <p>Review, search, or remove demo memories.</p>
          </div>
          <span className="memory-count">{memories.length} items</span>
        </div>

        <div className="memory-search">
          <Search size={17} />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search memories..."
            aria-label="Search memories"
          />
        </div>

        <div className="memory-list">
          {filteredMemories.map((memory) => (
            <article className="memory-item" key={memory.id}>
              <div className="memory-item-icon"><Lightbulb size={19} /></div>
              <div className="memory-item-body">
                <div className="memory-item-title">
                  <h4>{memory.title}</h4>
                  <span className="memory-category"><Tag size={11} /> {memory.category}</span>
                </div>
                <p>{memory.detail}</p>
                <span className="memory-date"><Clock3 size={12} /> {memory.date}</span>
              </div>
              <button
                className="memory-delete"
                onClick={() => deleteMemory(memory.id)}
                aria-label={`Delete ${memory.title}`}
                title="Delete memory"
              >
                <Trash2 size={16} />
              </button>
            </article>
          ))}

          {filteredMemories.length === 0 && (
            <div className="memory-empty">
              <Brain size={25} />
              <p>No memories found.</p>
              <span>Try another search or add a new memory.</span>
            </div>
          )}
        </div>
      </section>

      <p className="memory-disclaimer">
        Prototype only: these sample memories are held in the current page session.
        They are not connected to the AI agent or database yet.
      </p>
    </div>
  )
}

export default MemoryLab
