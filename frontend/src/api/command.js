import { createWS } from "./socket"

const URL = "/ws/tello/command"  // buildWSUrl이 절대URL로 변환

const q = []
let sending = false
let client = null

function enqueue(payload, priority = 5) {
  q.push({ priority, payload })
  q.sort((a, b) => a.priority - b.priority)
  drain()
}
async function drain() {
  if (sending || !client?.isOpen()) return
  sending = true
  while (q.length && client?.isOpen()) {
    const { payload } = q.shift()
    client.jsonSend({ type: "control", ...payload })
    await new Promise((r) => setTimeout(r, 40))
  }
  sending = false
}

export function connectCommandWS({ onAck, onError, onOpen } = {}) {
  client = createWS(URL, {
    onOpen,
    onMessage: (msg) => {
      if (!msg) return
      if (msg.type === "ack") { onAck && onAck(msg); return }
      if (typeof msg.ok !== "undefined") { onAck && onAck(msg); return }
      // 기타 메시지는 디버그
      if (msg.type || msg.message) console.log("[CMD WS]", msg)
    },
    onError,
  })
  return client
}
export function disconnectCommandWS() { client?.close(); client = null }

// High-level API (공통 가이드 네이밍 유지)
export function move(direction, speed = 50, priority = 5) { enqueue({ action:"move", direction, speed }, priority) }
export function yawCW(speed = 50, priority = 4)  { move("cw",  speed, priority) }
export function yawCCW(speed = 50, priority = 4) { move("ccw", speed, priority) }
export function up(speed = 50, priority = 3)    { move("up",  speed, priority) }
export function down(speed = 50, priority = 3)  { move("down",speed, priority) }
export function takeoff(priority = 1)   { enqueue({ action:"takeoff"   }, priority) }
export function land(priority = 0)      { enqueue({ action:"land"      }, priority) }
export function emergency(priority = 0) { enqueue({ action:"emergency" }, priority) }
