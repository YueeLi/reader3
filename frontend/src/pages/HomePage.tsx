import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <section className="home-page">
      <div className="home-hero">
        <div className="home-hero-copy">
          <p className="eyebrow">Reader3 Platform</p>
          <h1>Curate, transform, and ship the reading experience you want.</h1>
          <p className="subhead">
            Reader3 blends Libra, a living EPUB library, with a focused toolbelt
            for conversions, metadata extraction, and visual assets.
          </p>
          <div className="home-hero-actions">
            <Link className="accent-button" to="/libra">
              Enter Libra
            </Link>
            <Link className="ghost-button" to="/tools">
              Build with Tools
            </Link>
          </div>
          <div className="home-hero-metrics">
            <div className="metric-card">
              <span className="metric-label">Storage</span>
              <strong className="metric-value">Local-first</strong>
            </div>
            <div className="metric-card">
              <span className="metric-label">Pipeline</span>
              <strong className="metric-value">EPUB-native</strong>
            </div>
            <div className="metric-card">
              <span className="metric-label">Output</span>
              <strong className="metric-value">PDF + Markdown</strong>
            </div>
          </div>
        </div>
        <div className="home-hero-visual">
          <div className="hero-stack">
            <div className="hero-card card-primary">
              <p className="hero-card-eyebrow">Libra</p>
              <h3>Living shelves</h3>
              <p>
                Monitor new imports, track reading momentum, and keep covers,
                chapters, and annotations in one place.
              </p>
              <div className="hero-card-tags">
                <span>Collections</span>
                <span>Search</span>
                <span>Reading</span>
              </div>
            </div>
            <div className="hero-card card-secondary">
              <p className="hero-card-eyebrow">Tools</p>
              <h3>Conversion suite</h3>
              <p>
                Turn EPUBs into PDFs, Markdown notes, and asset packs for
                downstream publishing.
              </p>
              <div className="hero-card-tags">
                <span>PDF</span>
                <span>Markdown</span>
                <span>Assets</span>
              </div>
            </div>
            <div className="hero-card card-tertiary">
              <p className="hero-card-eyebrow">Workflow</p>
              <h3>Sync + publish</h3>
              <p>
                Keep everything local, then ship results to the systems you
                already use.
              </p>
            </div>
          </div>
          <div className="hero-orbit">
            <span>Import</span>
            <span>Refine</span>
            <span>Export</span>
          </div>
        </div>
      </div>

      <div className="home-panels">
        <article className="home-panel">
          <p className="eyebrow">Platform</p>
          <h2>One home for your reading stack.</h2>
          <p className="subhead">
            Libra is designed for teams that care about book quality, discoverability,
            and speed. Your library stays private and fast.
          </p>
        </article>
        <article className="home-panel">
          <p className="eyebrow">Automation</p>
          <h2>Automation without the guesswork.</h2>
          <p className="subhead">
            Every tool in the pipeline exposes a clean output, so you can move from
            EPUB to publishing-ready assets in minutes.
          </p>
        </article>
        <article className="home-panel">
          <p className="eyebrow">Craft</p>
          <h2>Designed for reading teams.</h2>
          <p className="subhead">
            Balanced typography, tactile motion, and a layout that puts books first.
          </p>
        </article>
      </div>

      <div className="home-flow">
        <div className="home-flow-header">
          <h2>How Reader3 moves a book through the pipeline</h2>
          <p className="subhead">
            Import, refine, and export without leaving the platform.
          </p>
        </div>
        <div className="home-flow-steps">
          <div className="flow-step">
            <span className="step-index">01</span>
            <h3>Drop in your EPUB</h3>
            <p>Reader3 indexes chapters, covers, and metadata automatically.</p>
          </div>
          <div className="flow-step">
            <span className="step-index">02</span>
            <h3>Route through Tools</h3>
            <p>Generate PDFs, Markdown notes, or image packs with one workflow.</p>
          </div>
          <div className="flow-step">
            <span className="step-index">03</span>
            <h3>Publish your stack</h3>
            <p>Export assets to your storage, CMS, or publishing pipeline.</p>
          </div>
        </div>
      </div>

      <div className="home-cta">
        <div>
          <p className="eyebrow">Ready to build?</p>
          <h2>Start with a new import or jump straight into Libra.</h2>
        </div>
        <div className="home-cta-actions">
          <Link className="accent-button" to="/tools">
            Launch Tools
          </Link>
          <Link className="ghost-button" to="/libra">
            Open Libra
          </Link>
        </div>
      </div>
    </section>
  );
}
