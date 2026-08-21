import { useEffect, type ReactNode } from "react";
import { useNavigate } from "@tanstack/react-router";

import { useAppStore } from "../stores/app-store";
import AppHeader from "./AppHeader";

type AppLayoutProps = {
  children: ReactNode;
  sidebar: ReactNode;
};

/** Shared authenticated page chrome; routes supply their own sidebar content. */
function AppLayout({ children, sidebar }: AppLayoutProps) {
  const navigate = useNavigate();
  const open = useAppStore((state) => state.sidebarOpen);
  const setSidebarOpen = useAppStore((state) => state.setSidebarOpen);
  const unauthorized = useAppStore((state) => state.unauthorized);
  const loadProjects = useAppStore((state) => state.loadProjects);

  useEffect(() => {
    void loadProjects();
  }, [loadProjects]);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setSidebarOpen(false);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [setSidebarOpen]);

  useEffect(() => {
    if (unauthorized) navigate({ to: "/login" });
  }, [unauthorized, navigate]);

  return (
    <>
      {open && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="bg-neutral/40 fixed inset-0 z-30 backdrop-blur-sm lg:hidden"
          aria-hidden="true"
        />
      )}
      {sidebar}
      <main
        className="min-h-screen transition-[padding] duration-300 lg:pl-64"
        style={open ? undefined : { paddingLeft: 0 }}
      >
        <div className="container mx-auto max-w-5xl px-4 pt-4 sm:px-6 sm:pt-6 lg:px-8">
          <AppHeader />
        </div>
        {children}
      </main>
    </>
  );
}

export default AppLayout;
