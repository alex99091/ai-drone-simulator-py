// 공통 WS 유틸
export function createWS(url, {
  onOpen, onMessage, onClose, onError,
  autoReconnect = true,
  backoffMs = [1000, 2000, 5000, 10000, 15000],
} = {}) {
  let ws = null;
  let closedByUser = false;
  let attempt = 0;

  const safeOnError = (ev) => { try { onError && onError(ev); } catch {} };
  const safeOnClose = (ev) => { try { onClose && onClose(ev); } catch {} };
  const safeOnOpen  = (ev) => { try { onOpen  && onOpen(ev);  } catch {} };
  const safeOnMsg   = (data, ev) => { try { onMessage && onMessage(data, ev); } catch {} };

  const connect = () => {
    if (!url || typeof url !== "string") {
      // URL 미설정: 일정 시간 후 재시도
      if (autoReconnect) {
        const wait = backoffMs[Math.min(attempt, backoffMs.length - 1)];
        attempt += 1; setTimeout(connect, wait);
      }
      return;
    }
    try {
      ws = new WebSocket(url);
    } catch (e) {
      safeOnError(e);
      if (autoReconnect) {
        const wait = backoffMs[Math.min(attempt, backoffMs.length - 1)];
        attempt += 1; setTimeout(connect, wait);
      }
      return;
    }

    ws.onopen = (ev) => { attempt = 0; safeOnOpen(ev); };
    ws.onmessage = (ev) => {
      let data = ev.data;
      try { data = JSON.parse(ev.data); } catch {}
      safeOnMsg(data, ev);
    };
    ws.onerror = (ev) => safeOnError(ev);
    ws.onclose = (ev) => {
      safeOnClose(ev);
      if (!closedByUser && autoReconnect) {
        const wait = backoffMs[Math.min(attempt, backoffMs.length - 1)];
        attempt += 1; setTimeout(connect, wait);
      }
    };
  };

  connect();

  return {
    send: (raw) => { try { if (ws?.readyState === WebSocket.OPEN) ws.send(raw); } catch {} },
    jsonSend: (obj) => { try { if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify(obj)); } catch {} },
    close: () => { closedByUser = true; try { ws?.close(); } catch {} },
    isOpen: () => ws?.readyState === WebSocket.OPEN,
  };
}
