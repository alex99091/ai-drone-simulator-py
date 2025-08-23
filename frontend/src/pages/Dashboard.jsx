import { useEffect, useMemo, useRef, useState } from "react";
import { connectCommandWS, move, yawCW, yawCCW, up, down, takeoff, land, emergency } from "../api/command";
import { startStatusPolling, connectStatusWS } from "../api/status";
import { getVideoUrl } from "../api/stream";

import { PathTrackerModel, PathTrackerCanvas } from "../tracking";

export default function Dashboard() {
  // 경로분석 모델 (컴포넌트 외부로 빼지 않고, 페이지 수준에서 주입)
  const trackerRef = useRef(new PathTrackerModel());
  const [, setVer] = useState(0); // 렌더 트리거

  const [telemetry, setTelemetry] = useState({
    battery: 0, height: 0, yaw: 0, pitch: 0, roll: 0, pos: { x: 0, y: 0, z: 0 },
    wifi: 0, speed: 0, traffic: "0 Mbps",
  });
  const [connectedCmd, setConnectedCmd] = useState(false);
  const [connectedSta, setConnectedSta] = useState(false);

  // 명령 WS (즉시 연결)
  useEffect(() => {
    const client = connectCommandWS({
      onOpen: () => setConnectedCmd(true),
      onError: () => setConnectedCmd(false),
    });
    return () => { client?.close(); setConnectedCmd(false); };
  }, []);

  // 상태: 10초 폴링이 기준, WS는 보조(있으면 수신)
  useEffect(() => {
    const stop = startStatusPolling((d) => {
      setTelemetry((p) => ({ ...p, ...d }));
      trackerRef.current.addTelemetry(d);
      setVer(trackerRef.current.version);
    }, 10000);

    const wsClient = connectStatusWS((msg) => {
      setTelemetry((p) => ({ ...p, ...msg }));
      trackerRef.current.addTelemetry(msg);
      setVer(trackerRef.current.version);
    }, {
      onOpen: () => setConnectedSta(true),
      onError: () => setConnectedSta(false),
    });

    return () => { stop(); wsClient?.close(); setConnectedSta(false); };
  }, []);

  // 마우스 컨트롤용 helper (명령 기록)
  const sendCmd = (payload) => {
    trackerRef.current.addCommand(payload);
    setVer(trackerRef.current.version);
    // 실제 송신
    const { action, direction, speed } = payload;
    if (action === "move") {
      if (direction === "cw") return yawCW(speed ?? 50);
      if (direction === "ccw") return yawCCW(speed ?? 50);
      if (direction === "up") return up(speed ?? 50);
      if (direction === "down") return down(speed ?? 50);
      return move(direction, speed ?? 50);
    }
    if (action === "takeoff") return takeoff(1);
    if (action === "land") return land(0);
    if (action === "emergency") return emergency(0);
  };

  const videoSrc = useMemo(() => getVideoUrl(), []);

  return (
    <div className="flex-1 bg-gray-900 text-gray-100 p-4 md:p-6 text-[0.8rem] md:text-[0.9rem]">
      <h1 className="text-lg md:text-xl font-bold mb-4 text-center">Monitoring Dashboard</h1>

      {/* 상단 카드 */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <Card title="Battery"><p className="text-green-400 font-bold">{telemetry.battery} %</p></Card>
        <Card title="Wifi"><p className="font-bold">{telemetry.wifi}</p></Card>
        <Card title="Speed"><p className="font-bold">{telemetry.speed} m/s</p></Card>
        <Card title="Height"><p className="font-bold">{telemetry.height} m</p></Card>
        <Card title="Cmd WS"><p className={`font-bold ${connectedCmd?"text-green-400":"text-red-400"}`}>{connectedCmd?"Connected":"Down"}</p></Card>
        <Card title="Status WS"><p className={`font-bold ${connectedSta?"text-green-400":"text-red-400"}`}>{connectedSta?"Connected":"Down"}</p></Card>

        <Card title="Network Traffic" className="col-span-2 md:col-span-3">
          <p className="font-bold text-blue-400">{telemetry.traffic}</p>
        </Card>
        <Card title="Yaw/Pitch/Roll" className="col-span-2 md:col-span-3">
          <p className="font-bold">{telemetry.yaw} / {telemetry.pitch} / {telemetry.roll}</p>
        </Card>
      </div>

      {/* 실시간 영상 */}
      <div className="mt-6 w-full rounded-xl overflow-hidden shadow bg-black">
        <img
          src={videoSrc}
          alt="Tello Live"
          className="w-full h-[260px] md:h-[320px] object-contain"
          draggable={false}
          onError={(e) => {
            // 스트림 실패 시 대체 표기
            e.currentTarget.style.display = "none";
            const parent = e.currentTarget.parentElement;
            if (parent && !parent.querySelector(".video-fallback")) {
              const div = document.createElement("div");
              div.className = "video-fallback flex items-center justify-center h-[260px] md:h-[320px] text-gray-400";
              div.textContent = "[Video stream not available]";
              parent.appendChild(div);
            }
          }}
        />
      </div>


      {/* 컨트롤: 마우스 전용 + 이륙/착륙/비상 */}
      <div className="mt-4 rounded-xl border border-gray-800 bg-gray-900 p-3">
        <div className="text-xs text-gray-400 mb-2">Controls (Mouse only)</div>
        <ControlPad onSend={sendCmd} />
        <div className="mt-3 flex flex-wrap gap-2">
          <Btn onClick={()=>sendCmd({ action:"takeoff" })} className="bg-emerald-600 hover:bg-emerald-700">Takeoff</Btn>
          <Btn onClick={()=>sendCmd({ action:"land" })} className="bg-rose-600 hover:bg-rose-700">Land</Btn>
          <Btn onClick={()=>sendCmd({ action:"emergency" })} className="bg-red-700 hover:bg-red-800">EMERGENCY</Btn>
        </div>
      </div>

      {/* 경로 트래킹 (분리된 뷰 컴포넌트) */}
      <div className="mt-4">
        <PathTrackerCanvas path={trackerRef.current.getPath(800)} height={200} />
      </div>
    </div>
  );
}

/* --- 보조 UI --- */
function Card({ title, children, className = "" }) {
  return (
    <div className={`bg-gray-800 rounded-xl shadow p-3 ${className}`}>
      <h2 className="font-semibold mb-1 text-gray-400 text-xs md:text-sm">{title}</h2>
      {children}
    </div>
  );
}
function Btn({ children, className = "", ...rest }) {
  return <button {...rest} className={`px-3 py-2 rounded-md text-xs md:text-sm font-semibold ${className}`} />;
}

/* --- 컨트롤 패드(마우스) --- */
function ControlPad({ onSend }) {
  const B = ({ children, onClick }) => (
    <button
      onClick={onClick}
      className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-xs md:text-sm hover:bg-gray-700 transition"
    >
      {children}
    </button>
  );
  return (
    <div className="flex flex-col items-center gap-2 select-none">
      <div className="grid grid-cols-3 gap-2">
        <div />
        <B onClick={() => onSend({ action:"move", direction:"forward", speed:50 })}>↑</B>
        <div />
        <B onClick={() => onSend({ action:"move", direction:"left", speed:50 })}>←</B>
        <div />
        <B onClick={() => onSend({ action:"move", direction:"right", speed:50 })}>→</B>
        <div />
        <B onClick={() => onSend({ action:"move", direction:"back", speed:50 })}>↓</B>
        <div />
      </div>
      <div className="flex flex-wrap gap-2">
        <B onClick={() => onSend({ action:"move", direction:"up", speed:50 })}>Up</B>
        <B onClick={() => onSend({ action:"move", direction:"down", speed:50 })}>Down</B>
        <B onClick={() => onSend({ action:"move", direction:"ccw", speed:50 })}>Yaw CCW</B>
        <B onClick={() => onSend({ action:"move", direction:"cw",  speed:50 })}>Yaw CW</B>
      </div>
    </div>
  );
}
