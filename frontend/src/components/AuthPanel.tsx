import { FormEvent, useState } from "react";
import { ApiError } from "../api/client";
import { useLoginMutation, useSignupMutation } from "../hooks/useApiQueries";

export function AuthPanel() {
  const [authView, setAuthView] = useState<"login" | "signup" | null>(null);
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const loginMutation = useLoginMutation();
  const signupMutation = useSignupMutation();

  const error = loginMutation.error ?? signupMutation.error;
  const isBusy = loginMutation.isPending || signupMutation.isPending;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (mode === "signup") {
      await signupMutation.mutateAsync({ email, password, full_name: fullName });
    }
    await loginMutation.mutateAsync({ email, password });
  }

  function openAuth(nextMode: "login" | "signup") {
    setMode(nextMode);
    setAuthView(nextMode);
  }

  if (authView) {
    return (
      <main className="auth-only-screen">
        <section className="auth-panel" id="signin">
          <button className="back-link" onClick={() => setAuthView(null)} type="button">
            Back to overview
          </button>
          <div>
            <p className="eyebrow">Workspace access</p>
            <h2>{mode === "login" ? "Welcome back." : "Start with your first document."}</h2>
          </div>

          <div className="segmented-control" aria-label="Authentication mode">
            <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")} type="button">
              Login
            </button>
            <button className={mode === "signup" ? "active" : ""} onClick={() => setMode("signup")} type="button">
              Signup
            </button>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            {mode === "signup" && (
              <label>
                <span>Full name</span>
                <input
                  autoComplete="name"
                  onChange={(event) => setFullName(event.target.value)}
                  required
                  value={fullName}
                />
              </label>
            )}
            <label>
              <span>Email</span>
              <input
                autoComplete="email"
                onChange={(event) => setEmail(event.target.value)}
                required
                type="email"
                value={email}
              />
            </label>
            <label>
              <span>Password</span>
              <input
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                minLength={8}
                onChange={(event) => setPassword(event.target.value)}
                required
                type="password"
                value={password}
              />
            </label>

            {error && <p className="form-error">{formatError(error)}</p>}
            <button disabled={isBusy} type="submit">
              {isBusy ? "Working..." : mode === "login" ? "Sign in" : "Create account"}
            </button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <main className="auth-screen">
      <header className="landing-nav">
        <a className="landing-brand" href="#top" aria-label="Veridian home">
          <span className="brand-mark">V</span>
          <span>Veridian RAG</span>
        </a>
        <nav aria-label="Landing">
          <a href="#how-it-works">How it works</a>
          <a href="#use-cases">Use cases</a>
          <a href="#faq">FAQ</a>
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
            <button type="button" onClick={() => openAuth("signup")}>
              Create workspace
            </button>
            <button className="secondary-action" type="button" onClick={() => openAuth("login")}>
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
          <button type="button" onClick={() => openAuth("signup")}>
            Create workspace
          </button>
          <button className="secondary-action" type="button" onClick={() => openAuth("login")}>
            Sign in
          </button>
        </div>
      </section>
    </main>
  );
}

function formatError(error: Error) {
  if (error instanceof ApiError && typeof error.payload === "object" && error.payload) {
    return Object.values(error.payload).flat().join(" ");
  }
  return error.message;
}
