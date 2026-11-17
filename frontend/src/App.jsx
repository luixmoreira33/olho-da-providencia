import React, { useEffect, useState } from 'react'

const statusColor = {
  Healthy: '#22c55e',
  Warning: '#eab308',
  Critical: '#ef4444',
  Degraded: '#f97316',
  Failed: '#ef4444',
  Unknown: '#6b7280',
  Unavailable: '#9ca3af',
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

function DeepLinks({ app, dark }) {
  const [links, setLinks] = useState(null)
  useEffect(() => {
    fetch(`/api/applications/${encodeURIComponent(app.name)}/deeplinks`)
      .then(r => r.json())
      .then(setLinks)
      .catch(() => {})
  }, [app.name])

  if (!links) return null
  return (
    <div style={{ marginTop: 12 }}>
      <strong>Links diretos:</strong>{' '}
      {Object.entries(links).map(([k, href]) => (
        <a key={k} href={href} target="_blank" rel="noreferrer"
           style={{ marginRight: 12, color: dark ? '#93c5fd' : '#2563eb' }}>
          {k}
        </a>
      ))}
    </div>
  )
}

function Timeline({ appName, dark }) {
  const [events, setEvents] = useState([])
  useEffect(() => {
    fetch(`/api/applications/${encodeURIComponent(appName)}/timeline`)
      .then(r => r.json())
      .then(d => setEvents(d.timeline || []))
      .catch(() => {})
  }, [appName])

  if (!events.length) return null
  return (
    <div style={{ marginTop: 16 }}>
      <h4 style={{ margin: '0 0 8px 0' }}>Timeline</h4>
      <ul style={{ fontSize: 13, paddingLeft: 20, color: dark ? '#d1d5db' : '#374151' }}>
        {events.slice(0, 8).map((e, i) => (
          <li key={i}>{e.created_at?.slice(0, 19)} — {e.overall_status}</li>
        ))}
      </ul>
    </div>
  )
}

function AppCard({ app, dark }) {
  const [expanded, setExpanded] = useState(false)
  const bg = dark ? '#1f2937' : 'white'
  const border = dark ? '#374151' : '#e5e7eb'
  const text = dark ? '#f9fafb' : 'inherit'
  const muted = dark ? '#9ca3af' : '#6b7280'

  return (
    <div style={{
      border: `1px solid ${border}`,
      borderRadius: '12px',
      padding: '16px',
      background: bg,
      color: text,
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      marginBottom: '16px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
           onClick={() => setExpanded(!expanded)}
           role="button" tabIndex={0}
           onKeyDown={e => e.key === 'Enter' && setExpanded(!expanded)}>
        <div>
          <h3 style={{ margin: '0 0 8px 0', fontSize: '18px' }}>{app.name}</h3>
          <p style={{ margin: 0, color: muted, fontSize: '14px' }}>{app.summary}</p>
        </div>
        <StatusBadge status={app.overall_status} />
      </div>

      {expanded && (
        <div style={{ marginTop: '16px', borderTop: `1px solid ${border}`, paddingTop: '16px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {app.k8s_okd && (
              <div>
                <h4 style={{ margin: '0 0 8px 0' }}>OKD</h4>
                <StatusBadge status={app.k8s_okd.status} />
                <p style={{ fontSize: '14px', margin: '8px 0 0 0' }}>Pods: {app.k8s_okd.pods_ready}/{app.k8s_okd.pods_desired}</p>
              </div>
            )}
            {app.k8s_eks && (
              <div>
                <h4 style={{ margin: '0 0 8px 0' }}>EKS</h4>
                <StatusBadge status={app.k8s_eks.status} />
                <p style={{ fontSize: '14px', margin: '8px 0 0 0' }}>Pods: {app.k8s_eks.pods_ready}/{app.k8s_eks.pods_desired}</p>
              </div>
            )}
            {app.elk && (
              <div>
                <h4 style={{ margin: '0 0 8px 0' }}>ELK</h4>
                <StatusBadge status={app.elk.status} />
                <p style={{ fontSize: '14px', margin: '8px 0 0 0' }}>Erros (1h): {app.elk.error_count_1h}</p>
              </div>
            )}
            {app.dynatrace && (
              <div>
                <h4 style={{ margin: '0 0 8px 0' }}>Dynatrace</h4>
                <StatusBadge status={app.dynatrace.status} />
                <p style={{ fontSize: '14px', margin: '8px 0 0 0' }}>Problemas: {app.dynatrace.open_problems}</p>
              </div>
            )}
            {app.aws && (
              <div style={{ gridColumn: '1 / -1', background: dark ? '#111827' : '#f8fafc', padding: 12, borderRadius: 8 }}>
                <h4 style={{ margin: '0 0 8px 0' }}>AWS ({app.aws.type?.toUpperCase()})</h4>
                <StatusBadge status={app.aws.status} />
                <pre style={{ fontSize: 13, margin: '8px 0 0 0', whiteSpace: 'pre-wrap' }}>
                  {JSON.stringify(app.aws.details, null, 2)}
                </pre>
              </div>
            )}
          </div>

          {app.ai_insight && (
            <div style={{ marginTop: 16, padding: 12, background: dark ? '#1e3a5f' : '#eff6ff', borderRadius: 8 }}>
              <strong>Análise de IA</strong>
              <p style={{ margin: '8px 0 0 0', fontSize: 14 }}>{app.ai_insight}</p>
            </div>
          )}

          <Timeline appName={app.name} dark={dark} />
          <DeepLinks app={app} dark={dark} />
        </div>
      )}
    </div>
  )
}

function AdminPanel({ dark }) {
  const [visible, setVisible] = useState('')
  const [mapping, setMapping] = useState('')
  const bg = dark ? '#1f2937' : '#f9fafb'
  const border = dark ? '#374151' : '#e5e7eb'

  return (
    <div style={{ marginBottom: 24, padding: 16, border: `1px solid ${border}`, borderRadius: 12, background: bg }}>
      <h2 style={{ marginTop: 0 }}>Administração</h2>

      <div style={{ marginBottom: 16 }}>
        <label style={{ fontSize: 14, fontWeight: 600 }}>Recursos visíveis (vírgula)</label>
        <textarea
          value={visible}
          onChange={e => setVisible(e.target.value)}
          placeholder="app1,app2,minha-instancia,cluster/service"
          style={{ width: '100%', minHeight: 50, padding: 8, borderRadius: 6, border: '1px solid #d1d5db', marginTop: 4 }}
        />
      </div>

      <div style={{ marginBottom: 16 }}>
        <label style={{ fontSize: 14, fontWeight: 600 }}>Mapeamento manual (app = recurso1,recurso2)</label>
        <textarea
          value={mapping}
          onChange={e => setMapping(e.target.value)}
          placeholder="payment-service = payment-api,payment-ec2&#10;user-api = user-service"
          style={{ width: '100%', minHeight: 60, padding: 8, borderRadius: 6, border: '1px solid #d1d5db', marginTop: 4 }}
        />
      </div>

      <button style={{ padding: '8px 16px', background: '#2563eb', color: 'white', border: 'none', borderRadius: 6, cursor: 'pointer' }}>
        Salvar configuração
      </button>
      <p style={{ fontSize: 12, color: '#9ca3af', marginTop: 8 }}>
        Wizard de primeiro uso e teste de conexão serão refinados na próxima iteração.
      </p>
    </div>
  )
}

function Wizard({ onClose, dark }) {
  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50
    }}>
      <div style={{ background: dark ? '#1f2937' : 'white', color: dark ? 'white' : 'inherit', padding: 24, borderRadius: 12, maxWidth: 480 }}>
        <h2 style={{ marginTop: 0 }}>Primeiro uso</h2>
        <ol style={{ fontSize: 14, lineHeight: 1.6 }}>
          <li>Configure as variáveis no <code>.env</code> (OKD, EKS, ELK, Dynatrace, AWS).</li>
          <li>Suba com <code>docker compose up</code>.</li>
          <li>Use a aba Admin para marcar o que aparece e mapear apps.</li>
          <li>Pronto — o painel já mostra o status consolidado.</li>
        </ol>
        <button onClick={onClose} style={{ marginTop: 12, padding: '8px 16px', background: '#2563eb', color: 'white', border: 'none', borderRadius: 6 }}>
          Entendi
        </button>
      </div>
    </div>
  )
}

export default function App() {
  const [apps, setApps] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAdmin, setShowAdmin] = useState(false)
  const [tvMode, setTvMode] = useState(false)
  const [dark, setDark] = useState(false)
  const [showWizard, setShowWizard] = useState(true)

  useEffect(() => {
    const load = () => {
      fetch('/api/applications')
        .then(r => r.json())
        .then(data => { setApps(data); setLoading(false) })
        .catch(() => setLoading(false))
    }
    load()
    const id = setInterval(load, 30000)
    return () => clearInterval(id)
  }, [])

  if (loading) return <div style={{ padding: 32, color: dark ? 'white' : 'inherit' }}>Carregando...</div>

  const pageBg = tvMode ? (dark ? '#0f172a' : '#111827') : (dark ? '#111827' : '#f3f4f6')
  const pageColor = dark || tvMode ? 'white' : 'inherit'

  return (
    <div style={{
      maxWidth: tvMode ? '100%' : 1100,
      margin: '0 auto',
      padding: tvMode ? 16 : 24,
      fontFamily: 'system-ui, sans-serif',
      background: pageBg,
      minHeight: '100vh',
      color: pageColor
    }}>
      {showWizard && <Wizard onClose={() => setShowWizard(false)} dark={dark} />}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ margin: 0 }}>Olho da Providência</h1>
        <div>
          <button onClick={() => setDark(!dark)} style={{ marginRight: 8, padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db', background: dark ? '#374151' : 'white', color: dark ? 'white' : 'inherit', cursor: 'pointer' }}>
            {dark ? 'Claro' : 'Escuro'}
          </button>
          <button onClick={() => setShowAdmin(!showAdmin)} style={{ marginRight: 8, padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db', background: dark ? '#374151' : 'white', color: dark ? 'white' : 'inherit', cursor: 'pointer' }}>
            Admin
          </button>
          <button onClick={() => setTvMode(!tvMode)} style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #d1d5db', background: dark ? '#374151' : 'white', color: dark ? 'white' : 'inherit', cursor: 'pointer' }}>
            {tvMode ? 'Sair TV' : 'Modo TV'}
          </button>
        </div>
      </div>

      {showAdmin && <AdminPanel dark={dark} />}

      <div style={{ display: 'grid', gridTemplateColumns: tvMode ? 'repeat(auto-fill, minmax(320px, 1fr))' : '1fr', gap: 16 }}>
        {apps.map(app => <AppCard key={app.name} app={app} dark={dark || tvMode} />)}
      </div>

      {apps.length === 0 && <p>Nenhuma aplicação encontrada. Verifique as conexões ou o modo demo.</p>}
    </div>
  )
}
