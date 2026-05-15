import { useState } from "react";

type LandingPageProps = {
  onOpenAuth: (mode: "login" | "signup") => void;
};

export function LandingPage({ onOpenAuth }: LandingPageProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  function openAuth(mode: "login" | "signup") {
    setIsMenuOpen(false);
    onOpenAuth(mode);
  }

  return (
    <main className="auth-screen">
      <header className="landing-nav">
        <a className="landing-brand" href="#top" aria-label="DocuMind AI home">
          <span className="brand-mark">D</span>
          <span>DocuMind AI</span>
        </a>
        <button
          aria-controls="landing-menu"
          aria-expanded={isMenuOpen}
          aria-label={isMenuOpen ? "Close menu" : "Open menu"}
          className={isMenuOpen ? "hamburger-button open" : "hamburger-button"}
          onClick={() => setIsMenuOpen((isOpen) => !isOpen)}
          type="button"
        >
          <span />
          <span />
          <span />
        </button>
        <nav className={isMenuOpen ? "open" : ""} id="landing-menu" aria-label="Landing">
          <a href="#how-it-works" onClick={() => setIsMenuOpen(false)}>
            How it works
          </a>
          <a href="#use-cases" onClick={() => setIsMenuOpen(false)}>
            Use cases
          </a>
          <a href="#faq" onClick={() => setIsMenuOpen(false)}>
            FAQ
          </a>
          <button className="nav-auth-button" onClick={() => openAuth("login")} type="button">
            Sign in
          </button>
        </nav>
      </header>

      <section className="landing-hero" id="top">
        <div className="landing-copy">
          <p className="eyebrow">Private document workspace</p>
          <h1>Read your files with a little more certainty.</h1>
          <p className="hero-copy">
            Upload PDFs, notes, and docs. Ask plain questions. Get answers that point back to the exact source text.
          </p>
          <div className="landing-actions">
            <button type="button" onClick={() => onOpenAuth("signup")}>
              Create workspace
            </button>
            <button className="secondary-action" type="button" onClick={() => onOpenAuth("login")}>
              Use existing account
            </button>
          </div>
          <div className="landing-proof" aria-label="Product highlights">
            <span>Grounded answers</span>
            <span>Citations included</span>
            <span>Local-first demo</span>
          </div>
        </div>

        <div className="product-preview" aria-label="Product preview">
          <div className="preview-toolbar">
            <span />
            <span />
            <span />
          </div>
          <div className="preview-body">
            <div className="preview-document">
              <small>Research brief.pdf</small>
              <strong>Q3 operational review</strong>
              <p>Customer support volume decreased after the onboarding update...</p>
            </div>
            <div className="preview-answer">
              <small>Answer</small>
              <p>The file says onboarding changes reduced support load and improved first-week activation.</p>
              <span>Source: page 2 · 91%</span>
            </div>
          </div>
        </div>
      </section>

      <section className="landing-details" id="how-it-works">
        <article>
          <span>01</span>
          <h2>Upload the material</h2>
          <p>Keep your source files in one calm workspace, ready for search and chat.</p>
        </article>
        <article>
          <span>02</span>
          <h2>Ask naturally</h2>
          <p>No query language. Ask the way you would ask a teammate who read the document.</p>
        </article>
        <article id="privacy">
          <span>03</span>
          <h2>Check the evidence</h2>
          <p>Every answer keeps citations close, so you can verify before trusting it.</p>
        </article>
      </section>

      <section className="landing-split" id="use-cases">
        <div>
          <p className="eyebrow">Built for actual reading</p>
          <h2>Useful when the answer has to come from the file, not a hunch.</h2>
        </div>
        <div className="use-case-list">
          <article>
            <h3>College and project work</h3>
            <p>Ask about synopsis files, reports, research PDFs, and keep the cited passage close.</p>
          </article>
          <article>
            <h3>Contracts and policies</h3>
            <p>Find obligations, dates, risk clauses, and exceptions without scanning the whole document.</p>
          </article>
          <article>
            <h3>Team knowledge</h3>
            <p>Turn messy notes into a searchable workspace that still respects the original source.</p>
          </article>
        </div>
      </section>

      <section className="landing-feature-band">
        <article>
          <strong>Source-aware answers</strong>
          <p>Every response is shaped around retrieved chunks and citations.</p>
        </article>
        <article>
          <strong>Simple document flow</strong>
          <p>Upload, wait for ready, select sources, ask. Nothing fussy.</p>
        </article>
        <article>
          <strong>Human review built in</strong>
          <p>The app shows supporting text so you can check before using an answer.</p>
        </article>
      </section>

      <section className="landing-faq" id="faq">
        <div>
          <p className="eyebrow">Quick answers</p>
          <h2>Before you start</h2>
        </div>
        <div className="faq-list">
          <article>
            <h3>What files can I upload?</h3>
            <p>PDF, DOCX, and TXT files are supported in this workspace.</p>
          </article>
          <article>
            <h3>Why are citations important?</h3>
            <p>They let you verify the exact evidence behind an answer instead of trusting a black box.</p>
          </article>
          <article>
            <h3>Can I ask broad questions?</h3>
            <p>Yes. Select a ready document and ask for summaries, dates, risks, obligations, or key points.</p>
          </article>
        </div>
      </section>

      <section className="landing-cta">
        <p className="eyebrow">Ready when you are</p>
        <h2>Bring one file. Ask one honest question.</h2>
        <div className="landing-actions">
          <button type="button" onClick={() => onOpenAuth("signup")}>
            Create workspace
          </button>
          <button className="secondary-action" type="button" onClick={() => onOpenAuth("login")}>
            Sign in
          </button>
        </div>
      </section>
    </main>
  );
}
