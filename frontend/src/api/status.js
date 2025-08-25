import { createWS } from "./socket"

const HTTP_BASE = import.meta.env.VITE_BACKEND_HTTP
const WS_BASE   = import.meta.env.VITE_BACKEND_WS

export async function getStatusOnce() {
  try {
    const res = await fetch(`${HTTP_BASE}/api/tello/status`)
    if (!res.ok) throw new Error(`status http ${res.status}`)
    return await res.json()
  } catch (e) {
    console.warn('[REST status] fail', e)
    return {}
  }
}

export function startStatusPolling(onData, intervalMs = 10000) {
  let timer = null
  const tick = async () => {
    try { onData && onData(await getStatusOnce()) } catch {}
    finally { timer = setTimeout(tick, intervalMs) }
  }
  tick()
  return () => { if (timer) clearTimeout(timer) }
}

export function connectStatusWS(onTelemetry, { onOpen, onError } = {}) {
  const urlPath = `/ws/tello/status`
  return createWS(urlPath, {
    onOpen,
    onMessage: (msg) => {
      if (!msg) return
      if (msg.type === 'snapshot' && msg.data) { onTelemetry && onTelemetry(msg.data); return }
      if (msg.type === 'telemetry' && msg.data) { onTelemetry && onTelemetry(msg.data); return }
      // 백엔드가 그냥 status JSON 보낼 때
      if (msg.battery || msg.height || msg.yaw || msg.pitch || msg.roll) {
        onTelemetry && onTelemetry(msg); return
      }
    },
    onError,
  })
}

// 선택: 최초 REST 성공 대기(영상 mount 지연)
export async function waitFirstStatus(ok = d => !!d) {
  for (let i=0;i<10;i++){ const d = await getStatusOnce(); if (ok(d)) return d; await new Promise(r=>setTimeout(r,700)) }
  return null
}
