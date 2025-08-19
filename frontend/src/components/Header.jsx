export default function Header() {
  return (
    <header className="flex items-center justify-between px-6 py-4 bg-gray-800 shadow-md">
      {/* 왼쪽 홈 버튼 */}
      <button className="text-gray-200 hover:text-white">🏠 Home</button>
      
      {/* 센터 타이틀 */}
      <h1 className="text-xl font-semibold text-white">
        DJI Tello & Python RealTime Server
      </h1>
      
      {/* 오른쪽은 비워둠 */}
      <div className="w-12" />
    </header>
  );
}
