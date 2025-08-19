export default function Sidebar() {
  return (
    <aside className="w-52 h-screen p-4 space-y-4 
                     bg-gray-700 shadow-lg rounded-r-xl">
      <nav className="flex flex-col space-y-2">
        <button className="text-gray-100 hover:bg-gray-600 rounded-md px-3 py-2 text-left">
          Dashboard
        </button>
        <button className="text-gray-100 hover:bg-gray-600 rounded-md px-3 py-2 text-left">
          Map
        </button>
      </nav>
    </aside>
  );
}
