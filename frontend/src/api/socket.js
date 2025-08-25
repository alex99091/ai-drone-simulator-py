const globalBag = (typeof window !== 'undefined')
  ? (window.__WSCLIENTS__ = window.__WSCLIENTS__ || new Map())
  : new Map()

function buildWSUrl(pathOrAbs) {
  if (!pathOrAbs) throw new Error('WS url required')
  if (pathOrAbs.startsWith('ws://') || pathOrAbs.startsWith('wss://')) return pathOrAbs
  const base = import.meta.env.VITE_BACKEND_WS
  if (!base) throw new Error('VITE_BACKEND_WS not set')
  return `${base}${pathOrAbs}`
}

export function createWS(urlOrPath, {
  onOpen, onMessage, onClose, onError,
  autoReconnect = true,
  backoffMs = [1000, 2000, 5000, 10000, 15000],
  heartbeatMs = 25000,   // 브라우저는 ping/pong 자동 응답. 여기선 noop 송신만.
} = {}) {
  const url = buildWSUrl(urlOrPath)
  // 싱글턴: 같은 URL이면 기존 커넥션 재사용
  if (globalBag.has(url)) return globalBag.get(url)

  let ws = null
  let closedByUser = false
  let attempt = 0
  let hbTimer = null

  const safe = (fn, ...args) => { try { fn && fn(...args) } catch {} }

  const connect = () => {
    try {
      ws = new WebSocket(url)
    } catch (e) {
      safe(onError, e)
      if (autoReconnect) scheduleReconnect()
      return
    }

    ws.onopen = (ev) => {
      attempt = 0
      // 하트비트(옵션): 서버가 너무 오래 idle이면 끊는 환경에서 유용
      if (heartbeatMs > 0) {
        hbTimer && clearInterval(hbTimer)
        hbTimer = setInterval(() => {
          try { if (ws?.readyState === WebSocket.OPEN) ws.send('') } catch {}
        }, heartbeatMs)
      }
      safe(onOpen, ev)
    }

    ws.onmessage = (ev) => {
      let data = ev.data
      try { data = JSON.parse(ev.data) } catch {}
      safe(onMessage, data, ev)
    }

    ws.onerror = (ev) => { safe(onError, ev) }

    ws.onclose = (ev) => {
      hbTimer && clearInterval(hbTimer); hbTimer = null
      safe(onClose, ev)
      if (!closedByUser && autoReconnect) scheduleReconnect()
    }
  }

  const scheduleReconnect = () => {
    const wait = backoffMs[Math.min(attempt, backoffMs.length - 1)]
    attempt += 1
    setTimeout(connect, wait)
  }

  connect()

  const client = {
    send: (raw) => { try { if (ws?.readyState === WebSocket.OPEN) ws.send(raw) } catch {} },
    jsonSend: (obj) => { try { if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify(obj)) } catch {} },
    close: () => { closedByUser = true; try { ws?.close() } catch {}; globalBag.delete(url) },
    isOpen: () => ws?.readyState === WebSocket.OPEN,
  }
  globalBag.set(url, client)
  // HMR 종료 시 자동 정리
  if (import.meta.hot) {
    import.meta.hot.dispose(() => { try { client.close() } catch {} })
  }
  return client
}
