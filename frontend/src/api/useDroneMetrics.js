import { useState, useEffect } from "react";

export function useDroneMetrics(pollingInterval = 5000) {
  const [metrics, setMetrics] = useState({
    battery: 0,
    wifi: 0,
    speed: 0,
    height: 0,
    traffic: "0 Mbps",
  });
  const [alertsOn, setAlertsOn] = useState(false);

  // 메트릭 주기적 fetch
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
    const interval = setInterval(fetchMetrics, pollingInterval);
    return () => clearInterval(interval);
  }, [pollingInterval]);

  // Alerts 토글
  const toggleAlerts = async (enabled) => {
    try {
      await fetch("/api/telegram-alerts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled }),
      });
      setAlertsOn(enabled);
    } catch (err) {
      console.error("Failed to toggle alerts", err);
    }
  };

  return { metrics, alertsOn, toggleAlerts };
}
