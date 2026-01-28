import { Route, Routes } from "react-router-dom";
import AppShell from "./AppShell";
import HomePage from "../pages/HomePage";
import LibraryPage from "../pages/LibraryPage";
import ReaderPage from "../pages/ReaderPage";
import NotFoundPage from "../pages/NotFoundPage";
import ToolsPage from "../pages/ToolsPage";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/libra" element={<LibraryPage />} />
        <Route path="/tools" element={<ToolsPage />} />
        <Route path="/read/:bookId/:chapterIndex" element={<ReaderPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AppShell>
  );
}
