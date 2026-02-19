import { useMemo, useState } from 'react'
import KPICard from './components/KPICard'
import { runSimulation } from './services/api'

const defaultData = { rounds: 0, leaderboard: [], results: [] }

export default function App() {
  const [data, setData] = useState(defaultData)
  const [loading, setLoading] = useState(false)

  const latest = useMemo(() => data.results[data.results.length - 1], [data.results])

  const handleRun = async () => {
    setLoading(true)
    try {
      const result = await runSimulation({ rounds: 3 })
      setData(result)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="container">
      <header>
        <h1>Hospital AI Survival Lab</h1>
        <button onClick={handleRun} disabled={loading}>{loading ? 'Running...' : 'Run Simulation (3 rounds)'}</button>
      </header>

      {latest && (
        <>
          <section className="grid">
            <KPICard label="Agent" value={latest.agent_name} />
            <KPICard label="Balance" value={`$${latest.metrics.balance}`} />
            <KPICard label="Burn Rate" value={`$${latest.metrics.burn_rate}/hr`} />
            <KPICard label="Profit Margin" value={`${(latest.metrics.profit_margin * 100).toFixed(2)}%`} />
            <KPICard label="Survival Time" value={`${latest.metrics.survival_time} hrs`} />
            <KPICard label="Door-to-Doctor" value={`${latest.kpis.door_to_doctor} hrs`} />
            <KPICard label="Length of Stay" value={`${latest.kpis.length_of_stay} hrs`} />
            <KPICard label="Throughput" value={latest.kpis.throughput} />
            <KPICard label="Error Rate" value={`${(latest.kpis.error_rate * 100).toFixed(1)}%`} />
          </section>

          <section className="panel">
            <h3>Leaderboard</h3>
            <pre>{JSON.stringify(data.leaderboard, null, 2)}</pre>
          </section>

          <section className="panel">
            <h3>Decision Logs (Latest Agent)</h3>
            <ul>
              {latest.decision_logs.map((log, idx) => (
                <li key={idx}>{log.action}: {log.reason} (ROI {log.expected_roi})</li>
              ))}
            </ul>
          </section>

          <section className="panel">
            <h3>Cost Breakdown</h3>
            <pre>{JSON.stringify(latest.cost_breakdown, null, 2)}</pre>
          </section>
        </>
      )}
    </main>
  )
}
