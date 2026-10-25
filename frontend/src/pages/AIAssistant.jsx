import { useState } from 'react'
import { Bot, Send, Sparkles, User, RotateCcw } from 'lucide-react'

const suggestions = [
  'Where did I spend the most?',
  'How can I save money this month?',
  'Summarise my recent expenses',
]

function AIAssistant() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hi! I'm your Expense Manager assistant. I can help you understand your spending and explore ways to manage your budget. What would you like to know?",
    },
  ])

  function sendMessage(text = input) {
    const trimmed = text.trim()
    if (!trimmed) return

    setMessages((previous) => [
      ...previous,
      { role: 'user', text: trimmed },
      {
        role: 'assistant',
        text: "This is a demo response. Once the backend is connected, I'll be able to analyse your actual expenses and provide personalised insights.",
      },
    ])
    setInput('')
  }

  return (
    <div className="chat-page">
      <div className="chat-heading">
        <div>
          <p className="eyebrow">YOUR PERSONAL FINANCE COMPANION</p>
          <h1>AI Assistant</h1>
          <p className="subtitle">Ask questions about your expenses, habits, and budget.</p>
        </div>
        <button
          className="chat-reset"
          onClick={() => setMessages([
            {
              role: 'assistant',
              text: "Hi! I'm your Expense Manager assistant. What would you like to know?",
            },
          ])}
        >
          <RotateCcw size={15} /> New chat
        </button>
      </div>

      <section className="chat-container">
        <div className="chat-status">
          <span className="assistant-avatar"><Bot size={21} /></span>
          <div><strong>Expense-Manager AI</strong><span><i /> Demo mode</span></div>
          <span className="sparkle"><Sparkles size={18} /></span>
        </div>

        <div className="chat-messages">
          {messages.map((message, index) => (
            <div className={`message-row ${message.role}`} key={index}>
              <div className="message-avatar">
                {message.role === 'assistant' ? <Bot size={18} /> : <User size={18} />}
              </div>
              <div className="message-content">
                <span className="message-author">
                  {message.role === 'assistant' ? 'Expense Manager AI' : 'You'}
                </span>
                <div className="message-bubble">{message.text}</div>
              </div>
            </div>
          ))}
        </div>

        {messages.length === 1 && (
          <div className="suggested-prompts">
            <p>TRY ASKING</p>
            <div>
              {suggestions.map((suggestion) => (
                <button key={suggestion} onClick={() => sendMessage(suggestion)}>
                  <Sparkles size={14} /> {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        <form
          className="chat-input-area"
          onSubmit={(event) => {
            event.preventDefault()
            sendMessage()
          }}
        >
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask anything about your spending..."
            aria-label="Message the Expense Manager assistant"
          />
          <button type="submit" disabled={!input.trim()} aria-label="Send message">
            <Send size={17} />
          </button>
        </form>
        <p className="chat-disclaimer">Demo responses only · AI insights will be enabled after backend integration.</p>
      </section>
    </div>
  )
}

export default AIAssistant
