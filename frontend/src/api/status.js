import { createWS } from "./socket";

const HTTP_BASE = import.meta.env.VITE_BACKEND_HTTP;
const WS_BASE   = import.meta.env.VITE_BACKEND_WS;

export async function getStatusOnce() {
  try {
    const res = await fetch(`${HTTP_BASE}/api/tello/status`);
    if (!res.ok) throw new Error(`status http ${res.status}`);
    return await res.json();
  } catch (e) {
    // 실패 시 빈 값 반환(페이지 유지)
    return {};
  }
}

// 폴링: 실패해도 다음 주기 계속
export function startStatusPolling(onData, intervalMs = 10000) {
  let timer = null;
  const tick = async () => {
    try {
      const d = await getStatusOnce();
      onData && onData(d);
    } catch {} finally {
      timer = setTimeout(tick, intervalMs);
    }
  };
  tick();
  return () => { if (timer) clearTimeout(timer); };
}

// (선택) WS 수신
export function connectStatusWS(onTelemetry, { onOpen, onError } = {}) {
  const url = `${WS_BASE}/ws/tello/status`;
  return createWS(url, {
    onOpen,
    onMessage: (msg) => { if (msg?.type === "telemetry") onTelemetry && onTelemetry(msg); },
    onError,
  });
}
