import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import ControlPage from "./pages/ControlPage";
import Map from "./pages/MapPage";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/map" element={<Map />} />
           <Route path="/control" element={<ControlPage />} />
        </Route>
      </Routes>
    </Router>
  );
}
