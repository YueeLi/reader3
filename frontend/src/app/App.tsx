import { Route, Routes } from "react-router-dom";
import AppShell from "./AppShell";
import LibraryPage from "../pages/LibraryPage";
import ReaderPage from "../pages/ReaderPage";
import NotFoundPage from "../pages/NotFoundPage";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<LibraryPage />} />
        <Route path="/read/:bookId/:chapterIndex" element={<ReaderPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AppShell>
  );
}
