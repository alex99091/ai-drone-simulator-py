import { useEffect, useState } from "react";
import { fetchMapData } from "../api/map";

export default function MapPage() {
  const [mapData, setMapData] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchMapData();
        setMapData(data);
      } catch (err) {
        console.error(err);
      }
    };
    load();
  }, []);

  if (!mapData) return <p className="text-gray-400">Loading map data...</p>;

  return (
    <div className="flex-1 bg-gray-900 p-6 text-gray-100">
      <h1 className="text-2xl font-bold mb-6 text-center">Map</h1>
      <div className="bg-gray-800 rounded-2xl shadow p-4 h-96 overflow-auto">
        {/* 단순히 데이터 찍기 */}
        <pre className="text-sm text-gray-300">{JSON.stringify(mapData, null, 2)}</pre>
      </div>
    </div>
  );
}