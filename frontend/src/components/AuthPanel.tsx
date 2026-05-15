import { FormEvent, useState } from "react";
import { ApiError } from "../api/client";
import { useLoginMutation, useSignupMutation } from "../hooks/useApiQueries";

type AuthPanelProps = {
  initialMode: "login" | "signup";
  onBack: () => void;
};

export function AuthPanel({ initialMode, onBack }: AuthPanelProps) {
  const [mode, setMode] = useState<"login" | "signup">(initialMode);
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

  return (
    <main className="auth-only-screen">
      <section className="auth-panel" id="signin">
        <button className="back-link" onClick={onBack} type="button">
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

function formatError(error: Error) {
  if (error instanceof ApiError && typeof error.payload === "object" && error.payload) {
    return Object.values(error.payload).flat().join(" ");
  }
  return error.message;
}
