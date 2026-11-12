import React, { useEffect, useState } from 'react'

const statusColor = {
  Healthy: '#22c55e',
  Warning: '#eab308',
  Critical: '#ef4444',
  Degraded: '#f97316',
  Failed: '#ef4444',
  HEALTHY: '#22c55e',
  UNHEALTHY: '#ef4444',
}

function StatusBadge({ status }) {
  return (
    <span style={{
      background: statusColor[status] || '#6b7280',
      color: 'white',
      padding: '4px 10px',
      borderRadius: '12px',
      fontSize: '12px',
      fontWeight: 'bold',
      textTransform: 'uppercase'
    }}>
      {status}
    </span>
  )
}

function AppCard({ app }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div style={{
      border: '1px solid #e5e7eb',
      borderRadius: '12px',
      padding: '16px',
      background: 'white',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      marginBottom: '16px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }} onClick={() => setExpanded(!expanded)}>
        <div>
          <h3 style={{ margin: '0 0 8px 0', fontSize: '18px' }}>{app.name}</h3>
          <p style={{ margin: 0, color: '#6b7280', fontSize: '14px' }}>{app.summary}</p>
        </div>
        <StatusBadge status={app.overall_status} />
      </div>

      {expanded && (
        <div style={{ marginTop: '16px', borderTop: '1px solid #e5e7eb', paddingTop: '16px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {app.k8s_okd && (
              <div>
                <h4 style={{ margin: '0 0 8px 0' }}>OKD</h4>
                <StatusBadge status={app.k8s_okd.status} />
                <p style={{ fontSize: '14px', margin: '8px 0 0 0' }}>
                  Pods: {app.k8s_okd.pods_ready}/{app.k8s_okd.pods_desired} • Restarts: {app.k8s_okd.restarts}
                </p>
              </div>
            )}
            {app.k8s_eks && (
              <div>
                <h4 style={{ margin: '0 0 8px 0' }}>EKS</h4>
                <StatusBadge status={app.k8s_eks.status} />
                <p style={{ fontSize: '14px', margin: '8px 0 0 0' }}>
                  Pods: {app.k8s_eks.pods_ready}/{app.k8s_eks.pods_desired} • Restarts: {app.k8s_eks.restarts}
                </p>
              </div>
            )}
            {app.elk && (
              <div>
                <h4 style={{ margin: '0 0 8px 0' }}>ELK (Logs)</h4>
                <StatusBadge status={app.elk.status} />
                <p style={{ fontSize: '14px', margin: '8px 0 0 0' }}>
                  Erros (1h): {app.elk.error_count_1h} • Warnings: {app.elk.warn_count_1h}
                </p>
                {app.elk.recent_errors.length > 0 && (
                  <ul style={{ fontSize: '13px', color: '#dc2626', margin: '8px 0 0 0', paddingLeft: '20px' }}>
                    {app.elk.recent_errors.map((err, i) => <li key={i}>{err}</li>)}
                  </ul>
                )}
              </div>
            )}
            {app.dynatrace && (
              <div>
                <h4 style={{ margin: '0 0 8px 0' }}>Dynatrace</h4>
                <StatusBadge status={app.dynatrace.status} />
                <p style={{ fontSize: '14px', margin: '8px 0 0 0' }}>
                  Problemas abertos: {app.dynatrace.open_problems} • Taxa de erro: {app.dynatrace.error_rate_percent}% • RT: {app.dynatrace.response_time_ms}ms
                </p>
              </div>
            )}
          </div>

          {app.ai_insight && (
            <div style={{
              marginTop: '16px',
              padding: '12px 16px',
              background: '#f0f9ff',
              border: '1px solid #bae6fd',
              borderRadius: '8px',
              fontSize: '14px',
              lineHeight: '1.5'
            }}>
              <strong style={{ color: '#0369a1' }}>Análise IA</strong>
              <p style={{ margin: '8px 0 0 0', whiteSpace: 'pre-line' }}>{app.ai_insight}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [apps, setApps] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetch('/api/applications')
      .then(r => r.json())
      .then(data => {
        setApps(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const filtered = apps.filter(a => {
    const matchStatus = filter === 'all' || a.overall_status.toLowerCase() === filter
    const matchSearch = a.name.toLowerCase().includes(search.toLowerCase())
    return matchStatus && matchSearch
  })

  const counts = {
    Healthy: apps.filter(a => a.overall_status === 'Healthy').length,
    Warning: apps.filter(a => a.overall_status === 'Warning').length,
    Critical: apps.filter(a => a.overall_status === 'Critical').length,
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px', fontFamily: 'system-ui, sans-serif', background: '#f9fafb', minHeight: '100vh' }}>
      <header style={{ marginBottom: '32px' }}>
        <h1 style={{ margin: '0 0 8px 0', fontSize: '28px' }}>Painel de Status por Aplicação</h1>
        <p style={{ margin: 0, color: '#6b7280' }}>Visão consolidada OKD • EKS • ELK • Dynatrace — objetiva para desenvolvedores</p>
      </header>

      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <div style={{ background: 'white', padding: '16px', borderRadius: '12px', minWidth: '140px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: statusColor.Healthy }}>{counts.Healthy}</div>
          <div style={{ color: '#6b7280' }}>Healthy</div>
        </div>
        <div style={{ background: 'white', padding: '16px', borderRadius: '12px', minWidth: '140px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: statusColor.Warning }}>{counts.Warning}</div>
          <div style={{ color: '#6b7280' }}>Warning</div>
        </div>
        <div style={{ background: 'white', padding: '16px', borderRadius: '12px', minWidth: '140px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: statusColor.Critical }}>{counts.Critical}</div>
          <div style={{ color: '#6b7280' }}>Critical</div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="Buscar aplicação..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ padding: '10px 14px', borderRadius: '8px', border: '1px solid #d1d5db', flex: 1, minWidth: '200px' }}
        />
        {['all', 'healthy', 'warning', 'critical'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '10px 16px',
              borderRadius: '8px',
              border: 'none',
              background: filter === f ? '#111827' : 'white',
              color: filter === f ? 'white' : '#374151',
              cursor: 'pointer',
              textTransform: 'capitalize',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}
          >
            {f === 'all' ? 'Todas' : f}
          </button>
        ))}
      </div>

      {loading ? (
        <p>Carregando status...</p>
      ) : filtered.length === 0 ? (
        <p>Nenhuma aplicação encontrada.</p>
      ) : (
        filtered.map(app => <AppCard key={app.name} app={app} />)
      )}

      <footer style={{ marginTop: '40px', color: '#9ca3af', fontSize: '13px' }}>
        Dados reais + análise de IA (quando configurada). Configure as conexões no backend via .env.
      </footer>
    </div>
  )
}
