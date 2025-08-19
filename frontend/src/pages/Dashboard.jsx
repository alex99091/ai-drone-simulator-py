import { useState, useEffect } from "react";

export default function Dashboard() {
  const [alertsOn, setAlertsOn] = useState(false);
  const [metrics, setMetrics] = useState({
    cpu: 0,
    memory: 0,
    disk: 0,
    traffic: "0 Mbps",
    status: "Loading...",
  });

  // metrics API 불러오기
  useEffect(() => {
    async function fetchMetrics() {
      try {
        const res = await fetch("/api/metrics");
        const data = await res.json();
        setMetrics(data);
      } catch (err) {
        console.error("Failed to fetch metrics", err);
      }
    }

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // 5초마다 새로고침
    return () => clearInterval(interval);
  }, []);

  // Alerts 토글 API
  const toggleAlerts = async (state) => {
    setAlertsOn(state);
    try {
      await fetch("/api/telegram-alerts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: state }),
      });
    } catch (err) {
      console.error("Failed to toggle alerts", err);
    }
  };

  return (
    <div className="flex-1 bg-gray-900 p-6 text-gray-100">
      <h1 className="text-2xl font-bold mb-6 text-center">
        Monitoring Dashboard
      </h1>

      {/* 주요 지표 그리드 */}
      <div className="grid grid-cols-4 gap-6">
        {/* 서버 상태 */}
        <div className="col-span-1 bg-gray-800 rounded-2xl shadow p-4">
          <h2 className="font-semibold mb-2 text-gray-400">Server Status</h2>
          <p className="text-green-400 font-bold">{metrics.status}</p>
        </div>

        {/* CPU */}
        <div className="col-span-1 bg-gray-800 rounded-2xl shadow p-4">
          <h2 className="font-semibold mb-2 text-gray-400">CPU Usage</h2>
          <p className="text-xl font-bold">{metrics.cpu}%</p>
        </div>

        {/* Memory */}
        <div className="col-span-1 bg-gray-800 rounded-2xl shadow p-4">
          <h2 className="font-semibold mb-2 text-gray-400">Memory Usage</h2>
          <p className="text-xl font-bold">{metrics.memory}%</p>
        </div>

        {/* Disk */}
        <div className="col-span-1 bg-gray-800 rounded-2xl shadow p-4">
          <h2 className="font-semibold mb-2 text-gray-400">Disk Usage</h2>
          <p className="text-xl font-bold">{metrics.disk}%</p>
        </div>

        {/* Network Traffic */}
        <div className="col-span-2 bg-gray-800 rounded-2xl shadow p-4">
          <h2 className="font-semibold mb-2 text-gray-400">Network Traffic</h2>
          <p className="text-xl font-bold text-blue-400">{metrics.traffic}</p>
        </div>

        {/* Alerts 토글 */}
        <div className="col-span-2 bg-gray-800 rounded-2xl shadow p-4">
          <h2 className="font-semibold text-gray-400 mb-3">Alerts</h2>
          <div className="flex gap-4">
            <button
              onClick={() => toggleAlerts(true)}
              className={`flex-1 py-2 rounded-lg font-bold transition ${
                alertsOn
                  ? "bg-green-500 text-white"
                  : "bg-gray-700 text-gray-300 hover:bg-green-600"
              }`}
            >
              Alerts ON
            </button>
            <button
              onClick={() => toggleAlerts(false)}
              className={`flex-1 py-2 rounded-lg font-bold transition ${
                !alertsOn
                  ? "bg-red-500 text-white"
                  : "bg-gray-700 text-gray-300 hover:bg-red-600"
              }`}
            >
              Alerts OFF
            </button>
          </div>
        </div>
      </div>

      {/* 지도 Placeholder */}
      <div className="mt-8 bg-gray-800 rounded-2xl shadow p-4 h-80 flex items-center justify-center">
        <p className="text-gray-400">[Map will be displayed here 🗺️]</p>
      </div>
    </div>
  );
}
