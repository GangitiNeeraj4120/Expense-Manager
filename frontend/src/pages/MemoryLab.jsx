import { useEffect, useState } from 'react'
import { Brain, Plus, Search, Trash2, Lightbulb, ShieldCheck, Clock3, Tag } from 'lucide-react'
import { getMemoryLabData, saveMemory, deleteMemory } from '../services/api'

const typeForCategory = {
  Preferences: 'preference',
  Budget: 'user_confirmed',
  Goals: 'user_confirmed',
  'Spending habits': 'observed_pattern',
}
const labelForType = {
  semantic: 'General',
  observed_pattern: 'Spending habits',
  user_confirmed: 'User confirmed',
  preference: 'Preferences',
}

function MemoryLab() {
  const [data, setData] = useState({ memories: [], insights: [], summary: { memory_count: 0, monthly_spending: 0 } })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [saving, setSaving] = useState(false)
  const [title, setTitle] = useState('')
  const [detail, setDetail] = useState('')
  const [category, setCategory] = useState('Preferences')

  async function loadData() {
    try {
      setError('')
      const result = await getMemoryLabData()
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [])

  const memories = data.memories || []
  const insights = data.insights || []
  const filteredMemories = memories.filter((memory) =>
    `${memory.condition || ''} ${memory.value || ''} ${memory.type || ''}`.toLowerCase().includes(search.toLowerCase())
  )

  async function addMemory(event) {
    event.preventDefault()
    if (!title.trim() || !detail.trim()) return
    setSaving(true)
    setError('')
    try {
      await saveMemory({
        type: typeForCategory[category] || 'preference',
        condition: title.trim(),
        value: detail.trim(),
        source: 'memory_lab',
        confidence: 0.9,
      })
      setTitle('')
      setDetail('')
      setCategory('Preferences')
      setShowForm(false)
      await loadData()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function removeMemory(memory) {
    if (!window.confirm(`Delete memory "${memory.condition}"?`)) return
    try {
      await deleteMemory(memory.id)
      await loadData()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="page-content memory-page">
      <section className="welcome-row">
        <div>
          <p className="eyebrow">PERSONALISED AI MEMORY</p>
          <h1>Memory Lab</h1>
          <p className="subtitle">Memories and patterns retrieved from your backend database.</p>
        </div>
        <button className="primary-button" onClick={() => setShowForm(!showForm)}><Plus size={16} style={{ verticalAlign: 'middle', marginRight: 5 }} />Add memory</button>
      </section>

      {error && <div className="panel" role="alert"><strong>Problem:</strong> {error}</div>}
      {loading ? <p>Loading memories from MongoDB...</p> : (
        <>
          <section className="memory-info-grid">
            <article className="panel memory-info-card"><div className="memory-info-icon"><Brain size={21} /></div><h3>{data.summary?.memory_count ?? memories.length}</h3><p>Stored memories</p></article>
            <article className="panel memory-info-card"><div className="memory-info-icon green"><ShieldCheck size={21} /></div><h3>{insights.length}</h3><p>Agent-observed patterns</p></article>
            <article className="panel memory-info-card"><div className="memory-info-icon orange"><Clock3 size={21} /></div><h3>MongoDB</h3><p>Persistent storage</p></article>
          </section>

          {insights.length > 0 && <section className="panel memories-panel">
            <div className="panel-heading"><div><h3>Insights from financial analysis</h3><p>Stored observations produced by the backend analysis workflow.</p></div></div>
            <div className="memory-list">{insights.map((memory) => <article className="memory-item" key={memory.id}><div className="memory-item-icon"><Lightbulb size={19} /></div><div className="memory-item-body"><div className="memory-item-title"><h4>{memory.condition}</h4><span className="memory-category"><Tag size={11} />Agent insight</span></div><p>{memory.value}</p><span className="memory-date"><Clock3 size={12} />{memory.created_at ? new Date(memory.created_at).toLocaleString() : 'Saved in database'}</span></div></article>)}</div>
          </section>}

          {showForm && <form className="panel memory-form" onSubmit={addMemory}>
            <h3>Create a persistent memory</h3>
            <label>Memory title<input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="e.g. Monthly food budget preference" required /></label>
            <label>Memory details<textarea value={detail} onChange={(event) => setDetail(event.target.value)} placeholder="What should the assistant remember?" rows={3} required /></label>
            <label>Category<select value={category} onChange={(event) => setCategory(event.target.value)}><option>Preferences</option><option>Budget</option><option>Goals</option><option>Spending habits</option></select></label>
            <div className="memory-form-actions"><button type="button" className="chat-reset" onClick={() => setShowForm(false)}>Cancel</button><button type="submit" className="primary-button" disabled={saving}>{saving ? 'Saving...' : 'Save to database'}</button></div>
          </form>}

          <section className="panel memories-panel">
            <div className="panel-heading"><div><h3>Remembered information</h3><p>These are active memories retrieved from the backend.</p></div><span className="memory-count">{memories.length} items</span></div>
            <div className="memory-search"><Search size={17} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search memories..." aria-label="Search memories" /></div>
            <div className="memory-list">
              {filteredMemories.map((memory) => <article className="memory-item" key={memory.id}>
                <div className="memory-item-icon"><Lightbulb size={19} /></div>
                <div className="memory-item-body"><div className="memory-item-title"><h4>{memory.condition}</h4><span className="memory-category"><Tag size={11} />{labelForType[memory.type] || memory.type}</span></div><p>{memory.value}</p><span className="memory-date"><Clock3 size={12} />{memory.created_at ? new Date(memory.created_at).toLocaleString() : 'Stored in database'} · Source: {memory.source || 'unknown'}</span></div>
                <button className="memory-delete" onClick={() => removeMemory(memory)} aria-label={`Delete ${memory.condition}`} title="Delete memory"><Trash2 size={16} /></button>
              </article>)}
              {filteredMemories.length === 0 && <div className="memory-empty"><Brain size={25} /><p>No stored memories found.</p><span>Run financial analysis or add a memory.</span></div>}
            </div>
          </section>
        </>
      )}
    </div>
  )
}

export default MemoryLab
