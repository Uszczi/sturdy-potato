import { useEffect } from "react";
import {
  Outlet,
  createFileRoute,
  redirect,
  useNavigate,
} from "@tanstack/react-router";
import Sidebar from "../components/Sidebar";
import { useAppStore } from "../stores/app-store";

export const Route = createFileRoute("/_app")({
  beforeLoad: ({ context, location }) => {
    if (!context.isAuthenticated()) {
      throw redirect({ to: "/login", search: { redirect: location.href } });
    }
  },
  component: AppLayout,
});

function AppLayout() {
  const navigate = useNavigate();
  const open = useAppStore((state) => state.sidebarOpen);
  const setSidebarOpen = useAppStore((state) => state.setSidebarOpen);
  const unauthorized = useAppStore((state) => state.unauthorized);
  const refresh = useAppStore((state) => state.refresh);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  // Escape closes the mobile drawer, matching the base template.
  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setSidebarOpen(false);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [setSidebarOpen]);

  // A rejected token flips the store into `unauthorized`; bounce to login.
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
      <Sidebar />
      <main
        className="min-h-screen transition-[padding] duration-300 lg:pl-64"
        style={open ? undefined : { paddingLeft: 0 }}
      >
        <Outlet />
      </main>
    </>
  );
}
