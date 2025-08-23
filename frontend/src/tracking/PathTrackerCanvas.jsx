import { useEffect, useRef } from "react";

/**
 * 순수 뷰: path 배열을 받아 캔버스에 궤적을 그립니다.
 * path: [{x,y,ts}]
 */
export default function PathTrackerCanvas({ path, height = 180 }) {
  const ref = useRef(null);

  useEffect(() => {
    const cvs = ref.current;
    const ctx = cvs.getContext("2d");
    const w = cvs.width, h = cvs.height;

    // 배경
    ctx.fillStyle = "#0f172a"; ctx.fillRect(0, 0, w, h);

    // 그리드
    ctx.strokeStyle = "#1f2937"; ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
    for (let y = 0; y < h; y += 40) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }

    if (!path || path.length < 2) return;

    // 스케일
    const xs = path.map(p => p.x), ys = path.map(p => p.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const dx = Math.max(1e-3, maxX - minX), dy = Math.max(1e-3, maxY - minY);
    const pad = 16;
    const s = Math.min((w - pad * 2) / dx, (h - pad * 2) / dy);
    const tx = (x) => pad + (x - minX) * s;
    const ty = (y) => h - pad - (y - minY) * s;

    // 경로
    ctx.strokeStyle = "#38bdf8"; ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(tx(path[0].x), ty(path[0].y));
    for (let i = 1; i < path.length; i++) ctx.lineTo(tx(path[i].x), ty(path[i].y));
    ctx.stroke();

    // 현재 위치
    const last = path[path.length - 1];
    ctx.fillStyle = "#f43f5e";
    ctx.beginPath(); ctx.arc(tx(last.x), ty(last.y), 4, 0, Math.PI * 2); ctx.fill();
  }, [path]);

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-3">
      <div className="text-xs text-gray-400 mb-1">Trajectory</div>
      <canvas ref={ref} width={800} height={height} className="w-full h-auto" />
    </div>
  );
}
