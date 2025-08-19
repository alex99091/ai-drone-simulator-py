import Header from "./Header";
import Sidebar from "./Sidebar";
import Footer from "./Footer";
import { Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <div className="flex min-h-screen bg-gray-900 text-gray-100">
      {/* 사이드바 */}
      <Sidebar />

      <div className="flex-1 flex flex-col">
        {/* 헤더 */}
        <Header />

        {/* 메인 컨텐츠 */}
        <main className="flex-1 p-6">
          <Outlet />
        </main>

        {/* 푸터 */}
        <Footer />
      </div>
    </div>
  );
}
