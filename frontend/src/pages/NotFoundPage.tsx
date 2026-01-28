import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <section className="empty-state">
      <h2>Page not found</h2>
      <p>The view you are looking for does not exist.</p>
      <Link className="accent-button" to="/">
        Back to home
      </Link>
    </section>
  );
}
