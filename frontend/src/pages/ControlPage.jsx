import { useEffect, useRef } from "react";

export default function ControlPage() {
  const videoRef = useRef(null);

  // 더미: 실제 백엔드 WebRTC/WS 연결 전
  useEffect(() => {
    // 여기에 나중에 WebRTC나 WebSocket으로 Tello 영상 스트림을 연결
    if (videoRef.current) {
      videoRef.current.src =
        "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"; // 더미 HLS 스트림
      videoRef.current.play().catch(() => {});
    }
  }, []);

  // 키보드 이벤트 더미
  useEffect(() => {
    const handleKey = (e) => {
      switch (e.key) {
        case "ArrowUp":ㄴ
          console.log("Forward");
          break;
        case "ArrowDown":
          console.log("Backward");
          break;
        case "ArrowLeft":
          console.log("Left");
          break;
        case "ArrowRight":
          console.log("Right");
          break;
        default:
          break;
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  return (
    <div className="flex flex-col items-center">
      <h2 className="text-2xl font-bold mb-4">Drone Control</h2>

      {/* 드론 카메라 화면 */}
      <div className="w-[640px] h-[360px] bg-black rounded-lg shadow-lg mb-6">
        <video
          ref={videoRef}
          className="w-full h-full object-cover rounded-lg"
          autoPlay
          muted
          controls={false}
        />
      </div>

      {/* 방향키 UI */}
      <div className="grid grid-cols-3 gap-2">
        <div />
        <button className="px-4 py-2 bg-gray-700 text-white rounded-lg shadow">
          ↑
        </button>
        <div />

        <button className="px-4 py-2 bg-gray-700 text-white rounded-lg shadow">
          ←
        </button>
        <div />
        <button className="px-4 py-2 bg-gray-700 text-white rounded-lg shadow">
          →
        </button>

        <div />
        <button className="px-4 py-2 bg-gray-700 text-white rounded-lg shadow">
          ↓
        </button>
        <div />
      </div>
    </div>
  );
}
