import { Outlet, createFileRoute, redirect } from "@tanstack/react-router";
import AppLayout from "../components/AppLayout";
import Sidebar from "../components/Sidebar";

export const Route = createFileRoute("/_app")({
  beforeLoad: ({ context, location }) => {
    if (!context.isAuthenticated()) {
      throw redirect({ to: "/login", search: { redirect: location.href } });
    }
  },
  component: AppRouteLayout,
});

function AppRouteLayout() {
  return (
    <AppLayout sidebar={<Sidebar />}>
      <Outlet />
    </AppLayout>
  );
}
