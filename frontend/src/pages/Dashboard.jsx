import { useDroneMetrics } from "../api/useDroneMetrics";

export default function Dashboard() {
  const { metrics, alertsOn, toggleAlerts } = useDroneMetrics();

  return (
    <div className="flex-1 bg-gray-900 p-6 text-gray-100">
      <h1 className="text-2xl font-bold mb-6 text-center">
        Monitoring Dashboard
      </h1>

      {/* 주요 지표 */}
      <div className="grid grid-cols-4 gap-6">
        {/* Battery */}
        <div className="col-span-1 bg-gray-800 rounded-2xl shadow p-4">
          <h2 className="font-semibold mb-2 text-gray-400">Battery</h2>
          <p className="text-green-400 font-bold">{metrics.battery} %</p>
        </div>

        {/* Wifi */}
        <div className="col-span-1 bg-gray-800 rounded-2xl shadow p-4">
          <h2 className="font-semibold mb-2 text-gray-400">Wifi</h2>
          <p className="text-xl font-bold">{metrics.wifi}</p>
        </div>

        {/* Speed */}
        <div className="col-span-1 bg-gray-800 rounded-2xl shadow p-4">
          <h2 className="font-semibold mb-2 text-gray-400">Speed</h2>
          <p className="text-xl font-bold">{metrics.speed} m/s</p>
        </div>

        {/* Height */}
        <div className="col-span-1 bg-gray-800 rounded-2xl shadow p-4">
          <h2 className="font-semibold mb-2 text-gray-400">Height</h2>
          <p className="text-xl font-bold">{metrics.height} m</p>
        </div>

        {/* Network */}
        <div className="col-span-2 bg-gray-800 rounded-2xl shadow p-4">
          <h2 className="font-semibold mb-2 text-gray-400">Network Traffic</h2>
          <p className="text-xl font-bold text-blue-400">{metrics.traffic}</p>
        </div>

        {/* Alerts */}
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
