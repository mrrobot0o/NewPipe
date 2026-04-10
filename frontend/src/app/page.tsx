'use client'

import { useState } from 'react'
import { Play, Pause, RotateCcw, Sparkles, Users, Brain, Zap, Activity, MessageSquare, ChevronRight } from 'lucide-react'
import AgentChat from '../components/AgentChat'

export default function Dashboard() {
  const [simulationRunning, setSimulationRunning] = useState(false)
  const [progress, setProgress] = useState(0)
  const [agentCount, setAgentCount] = useState(100)
  const [maxRounds, setMaxRounds] = useState(40)
  const [activeAgent, setActiveAgent] = useState<any>(null)

  const stats = {
    totalAgents: agentCount,
    interactions: Math.floor(progress * agentCount * 10),
    consensus: progress * 0.87,
    timeElapsed: Math.floor(progress * 120), // seconds
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 via-slate-900 to-gray-950">
      {/* Header */}
      <header className="glass border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teresa-500 to-purple-600 flex items-center justify-center glow-blue">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">Teresa</h1>
              <p className="text-xs text-gray-400">Swarm Intelligence Engine v0.1.0</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-gray-300">
              <div className={`w-2 h-2 rounded-full ${simulationRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
              {simulationRunning ? 'Simulation Active' : 'Ready'}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <StatCard icon={Users} label="Agents" value={stats.totalAgents} color="blue" />
          <StatCard icon={Activity} label="Interactions" value={stats.interactions} color="purple" />
          <StatCard icon={Brain} label="Consensus" value={`${(stats.consensus * 100).toFixed(1)}%`} color="cyan" />
          <StatCard icon={Zap} label="Time" value={`${Math.floor(stats.timeElapsed / 60)}m ${stats.timeElapsed % 60}s`} color="yellow" />
        </div>

        {/* Control Panel */}
        <div className="glass rounded-2xl p-6 mb-8">
          <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
            <Brain className="w-5 h-5 text-teresa-500" />
            Simulation Control
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Agent Count</label>
              <input
                type="number"
                value={agentCount}
                onChange={(e) => setAgentCount(parseInt(e.target.value))}
                className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-3 focus:border-teresa-500 focus:outline-none"
                min="10"
                max="10000"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Max Rounds</label>
              <input
                type="number"
                value={maxRounds}
                onChange={(e) => setMaxRounds(parseInt(e.target.value))}
                className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-4 py-3 focus:border-teresa-500 focus:outline-none"
                min="10"
                max="200"
              />
            </div>
            <div className="flex items-end gap-3">
              <button
                onClick={() => setSimulationRunning(!simulationRunning)}
                className="flex-1 bg-gradient-to-r from-teresa-500 to-purple-600 hover:from-teresa-600 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-lg flex items-center justify-center gap-2 transition-all"
              >
                {simulationRunning ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                {simulationRunning ? 'Pause' : 'Start Simulation'}
              </button>
              <button
                onClick={() => { setProgress(0); setSimulationRunning(false) }}
                className="bg-gray-800 hover:bg-gray-700 text-white font-semibold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all"
              >
                <RotateCcw className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          {simulationRunning && (
            <div className="mt-6">
              <div className="flex justify-between text-sm text-gray-400 mb-2">
                <span>Round {Math.floor(progress * maxRounds)} / {maxRounds}</span>
                <span>{(progress * 100).toFixed(0)}%</span>
              </div>
              <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-teresa-500 via-purple-600 to-pink-500 transition-all duration-300"
                  style={{ width: `${progress * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Visualization Area */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Agent Network */}
          <div className="glass rounded-2xl p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Users className="w-5 h-5 text-teresa-500" />
              Agent Network
            </h3>
            <div className="aspect-square bg-gray-900/50 rounded-xl flex items-center justify-center relative overflow-hidden">
              {/* Simulated network visualization */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative w-48 h-48">
                  {[...Array(12)].map((_, i) => (
                    <div
                      key={i}
                      className="absolute w-3 h-3 rounded-full bg-teresa-500/60 animate-float"
                      style={{
                        left: `${30 + Math.sin(i * 0.8) * 30}%`,
                        top: `${30 + Math.cos(i * 0.8) * 30}%`,
                        animationDelay: `${i * 0.1}s`,
                      }}
                    />
                  ))}
                  {/* Connection lines */}
                  <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
                    {[...Array(15)].map((_, i) => (
                      <line
                        key={i}
                        x1={`${30 + Math.sin(i * 0.8) * 30}`}
                        y1={`${30 + Math.cos(i * 0.8) * 30}`}
                        x2={`${30 + Math.sin((i + 1) * 0.8) * 30}`}
                        y2={`${30 + Math.cos((i + 1) * 0.8) * 30}`}
                        stroke="rgba(14, 165, 233, 0.2)"
                        strokeWidth="0.5"
                      />
                    ))}
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* Consensus Chart */}
          <div className="glass rounded-2xl p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Brain className="w-5 h-5 text-teresa-500" />
              Consensus Evolution
            </h3>
            <div className="aspect-square bg-gray-900/50 rounded-xl p-4 flex items-center justify-center">
              {/* Simulated consensus chart */}
              <div className="w-full h-full flex items-end gap-2">
                {[...Array(20)].map((_, i) => (
                  <div
                    key={i}
                    className="flex-1 bg-gradient-to-t from-teresa-600 to-teresa-400 rounded-t-sm transition-all duration-500"
                    style={{
                      height: `${20 + (Math.sin(i * 0.3) + 1) * 30 + progress * 30}%`,
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Agent List & Chat */}
        <div className="glass rounded-2xl p-6 mt-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-teresa-500" />
            Agents — Click to Chat
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { name: 'Ada Chen', role: 'analyst', id: 'a1' },
              { name: 'Marcus Silva', role: 'optimist', id: 'a2' },
              { name: 'Yuki Tanaka', role: 'skeptic', id: 'a3' },
              { name: 'Omar Patel', role: 'innovator', id: 'a4' },
              { name: 'Elena Novak', role: 'pragmatist', id: 'a5' },
              { name: 'Raj Fischer', role: 'critic', id: 'a6' },
              { name: 'Sofia Reyes', role: 'diplomat', id: 'a7' },
              { name: 'Claude Müller', role: 'visionary', id: 'a8' },
            ].map(agent => (
              <button
                key={agent.id}
                onClick={() => setActiveAgent(agent)}
                className="glass rounded-xl p-3 text-left hover:border-teresa-500/50 transition-all group"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{agent.name}</p>
                    <p className={`text-xs ${
                      ['text-blue-400','text-yellow-400','text-red-400','text-purple-400','text-green-400','text-orange-400','text-cyan-400','text-pink-400'][
                        ['analyst','optimist','skeptic','innovator','pragmatist','critic','diplomat','visionary'].indexOf(agent.role)
                      ] || 'text-gray-400'
                    }`}>{agent.role}</p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-teresa-500 transition-colors" />
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Event Log */}
        <div className="glass rounded-2xl p-6 mt-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-teresa-500" />
            Event Log
          </h3>
          <div className="space-y-2 font-mono text-sm">
            <div className="text-gray-500 flex gap-4">
              <span>[23:45:12]</span>
              <span className="text-teresa-400">Agents initialized</span>
            </div>
            <div className="text-gray-500 flex gap-4">
              <span>[23:45:14]</span>
              <span className="text-teresa-400">Social graph built</span>
            </div>
            <div className="text-gray-500 flex gap-4">
              <span>[23:45:15]</span>
              <span className="text-teresa-400">Round 1 started - 1,200 interactions</span>
            </div>
            {simulationRunning && (
              <div className="text-teresa-400 flex gap-4 animate-pulse-slow">
                <span>[--:--:--]</span>
                <span>Simulation in progress...</span>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

function StatCard({ icon: Icon, label, value, color }: { icon: any, label: string, value: number | string, color: string }) {
  const colorClasses = {
    blue: 'text-blue-400',
    purple: 'text-purple-400',
    cyan: 'text-cyan-400',
    yellow: 'text-yellow-400',
  }

  return (
    <div className="glass rounded-xl p-5">
      <div className="flex items-center gap-3 mb-3">
        <Icon className={`w-5 h-5 ${colorClasses[color as keyof typeof colorClasses]}`} />
        <span className="text-sm text-gray-400">{label}</span>
      </div>
      <div className={`text-3xl font-bold ${colorClasses[color as keyof typeof colorClasses]}`}>
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>

      {/* Agent Chat Modal */}
      {activeAgent && (
        <AgentChat
          agentId={activeAgent.id}
          agentName={activeAgent.name}
          agentRole={activeAgent.role}
          personality={{
            openness: 0.6,
            conscientiousness: 0.7,
            extraversion: 0.5,
            agreeableness: 0.6,
            neuroticism: 0.4,
          }}
          onClose={() => setActiveAgent(null)}
        />
      )}
    </div>
  )
}
