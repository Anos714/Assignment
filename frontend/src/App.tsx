import { useState } from "react";
import { AuthPanel } from "./components/AuthPanel";
import { DashboardPage } from "./components/DashboardPage";
import { LandingPage } from "./components/LandingPage";
import { useAppStore } from "./store/useAppStore";

type PublicView = "landing" | "login" | "signup";

function App() {
  const [publicView, setPublicView] = useState<PublicView>("landing");
  const accessToken = useAppStore((state) => state.accessToken);

  if (accessToken) {
    return <DashboardPage />;
  }

  if (publicView === "login" || publicView === "signup") {
    return <AuthPanel initialMode={publicView} onBack={() => setPublicView("landing")} />;
  }

  return <LandingPage onOpenAuth={setPublicView} />;
}

export default App;
