import React from 'react'
import { createRoot } from 'react-dom/client'

function App() {
  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 640, margin: '40px auto' }}>
      <h1>GoCare Voice Demo</h1>
      <p>Connect to a LiveKit room and talk to the agent.</p>
      <ol>
        <li>Generate a LiveKit access token on your server.</li>
        <li>Open this page with a URL like: <code>?url=wss://your-livekit&token=YOUR_TOKEN</code></li>
      </ol>
      <ConnectForm />
    </div>
  )
}

function ConnectForm() {
  const [url, setUrl] = React.useState<string>(() => new URLSearchParams(location.search).get('url') || '')
  const [token, setToken] = React.useState<string>(() => new URLSearchParams(location.search).get('token') || '')

  const handleConnect = React.useCallback(() => {
    if (!url || !token) {
      alert('Please provide url and token')
      return
    }
    const target = `${location.origin}${location.pathname}#connect:${encodeURIComponent(url)}:${encodeURIComponent(token)}`
    location.replace(target)
    location.reload()
  }, [url, token])

  return (
    <div style={{ display: 'grid', gap: 8 }}>
      <input placeholder="LiveKit URL" value={url} onChange={(e) => setUrl(e.target.value)} />
      <input placeholder="Access Token" value={token} onChange={(e) => setToken(e.target.value)} />
      <button onClick={handleConnect}>Connect</button>
      <RoomView />
    </div>
  )
}

function RoomView() {
  const [connected, setConnected] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [hashState, setHashState] = React.useState<string>(location.hash)

  React.useEffect(() => {
    const onHash = () => setHashState(location.hash)
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  React.useEffect(() => {
    const match = location.hash.match(/^#connect:([^:]+):(.+)$/)
    if (!match) return
    const [, urlEnc, tokenEnc] = match
    const url = decodeURIComponent(urlEnc)
    const token = decodeURIComponent(tokenEnc)

    import('livekit-client').then(async ({ Room, RoomEvent, createLocalAudioTrack }) => {
      const room = new Room()
      room.on(RoomEvent.Disconnected, () => setConnected(false))
      try {
        const mic = await createLocalAudioTrack()
        await room.connect(url, token)
        await room.localParticipant.publishTrack(mic)
        setConnected(true)
      } catch (e: any) {
        setError(String(e?.message || e))
      }
    })
  }, [hashState])

  if (error) return <p style={{ color: 'crimson' }}>Error: {error}</p>
  if (!connected) return <p>Not connected</p>
  return <p>Connected. Speak to the agent in the room.</p>
}

createRoot(document.getElementById('root')!).render(<App />)