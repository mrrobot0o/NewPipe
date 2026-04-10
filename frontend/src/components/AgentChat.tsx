'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles, X } from 'lucide-react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  agent_name?: string
  agent_role?: string
  timestamp?: string
}

interface AgentChatProps {
  agentId: string
  agentName: string
  agentRole: string
  personality: Record<string, number>
  onClose: () => void
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function AgentChat({ agentId, agentName, agentRole, personality, onClose }: AgentChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${API_BASE}/api/v1/agents/${agentId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: agentId,
          message: input,
        }),
      })

      const data = await res.json()

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response || data.error || 'No response',
        agent_name: data.agent_name,
        agent_role: data.agent_role,
        timestamp: data.timestamp,
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `[Connection error - LLM not configured]`,
      }])
    } finally {
      setLoading(false)
    }
  }

  const roleColors: Record<string, string> = {
    analyst: 'text-blue-400',
    optimist: 'text-yellow-400',
    skeptic: 'text-red-400',
    innovator: 'text-purple-400',
    pragmatist: 'text-green-400',
    critic: 'text-orange-400',
    diplomat: 'text-cyan-400',
    visionary: 'text-pink-400',
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="glass rounded-2xl w-full max-w-lg h-[600px] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teresa-500 to-purple-600 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold">{agentName}</h3>
              <p className={`text-xs ${roleColors[agentRole] || 'text-gray-400'}`}>
                {agentRole}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-20">
              <Sparkles className="w-8 h-8 mx-auto mb-3 text-teresa-500/50" />
              <p>Start a conversation with {agentName}</p>
              <p className="text-xs mt-1">This agent has a {agentRole} personality</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-teresa-500 to-purple-600 flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-teresa-600/30 border border-teresa-500/30'
                  : 'bg-gray-800/50 border border-white/10'
              }`}>
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                {msg.timestamp && (
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </p>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0 mt-1">
                  <User className="w-4 h-4 text-gray-300" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-teresa-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-gray-800/50 border border-white/10 rounded-2xl px-4 py-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-teresa-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-teresa-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-teresa-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-white/10">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder={`Message ${agentName}...`}
              className="flex-1 bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-sm focus:border-teresa-500 focus:outline-none"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-gradient-to-r from-teresa-500 to-purple-600 hover:from-teresa-600 hover:to-purple-700 disabled:opacity-50 text-white rounded-xl px-4 py-3 transition-all"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
