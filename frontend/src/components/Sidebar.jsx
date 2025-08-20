import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <aside className="w-52 h-screen p-4 space-y-4 
                     bg-gray-700 shadow-lg rounded-r-xl">
      <nav>
        <ul className="flex flex-col space-y-2">
          <li>
            <Link
              to="/"
              className="block text-gray-100 hover:bg-gray-600 rounded-md px-3 py-2"
            >
              Dashboard
            </Link>
          </li>
          <li>
            <Link
              to="/map"
              className="block text-gray-100 hover:bg-gray-600 rounded-md px-3 py-2"
            >
              Map
            </Link>
          </li>
          <li>
            <Link
              to="/control"
              className="block text-gray-100 hover:bg-gray-600 rounded-md px-3 py-2"
            >
              Control
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
