import { createWS } from "./socket";

const WS_BASE = import.meta.env.VITE_BACKEND_WS;
const URL = `${WS_BASE}/ws/tello/command`;

const q = [];
let sending = false;
let client = null;

function enqueue(payload, priority = 5) {
  q.push({ priority, payload });
  q.sort((a, b) => a.priority - b.priority); // 낮을수록 먼저
  drain();
}
async function drain() {
  if (sending || !client?.isOpen()) return;
  sending = true;
  while (q.length && client?.isOpen()) {
    const { payload } = q.shift();
    client.jsonSend({ type: "control", ...payload });
    await new Promise((r) => setTimeout(r, 40)); // 과도한 전송 방지
  }
  sending = false;
}

export function connectCommandWS({ onAck, onError, onOpen } = {}) {
  client = createWS(URL, {
    onOpen,
    onMessage: (msg) => {
      if (msg && (msg.type === "ack" || msg.ok !== undefined)) onAck && onAck(msg);
    },
    onError,
  });
  return client;
}
export function disconnectCommandWS() { client?.close(); client = null; }

// 고수준 API
export function move(direction, speed = 50, priority = 5) { enqueue({ action:"move", direction, speed }, priority); }
export function yawCW(speed = 50, priority = 4)  { move("cw",  speed, priority); }
export function yawCCW(speed = 50, priority = 4) { move("ccw", speed, priority); }
export function up(speed = 50, priority = 3)    { move("up",  speed, priority); }
export function down(speed = 50, priority = 3)  { move("down",speed, priority); }

export function takeoff(priority = 1)   { enqueue({ action:"takeoff"   }, priority); }
export function land(priority = 0)      { enqueue({ action:"land"      }, priority); }
export function emergency(priority = 0) { enqueue({ action:"emergency" }, priority); }
