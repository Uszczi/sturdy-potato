import { Outlet, createRootRouteWithContext } from "@tanstack/react-router";
import ThemeToggle from "../components/ThemeToggle";

export type RouterContext = {
  isAuthenticated: () => boolean;
};

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

function RootLayout() {
  return (
    <>
      <div className="fixed right-4 top-4 z-50">
        <ThemeToggle />
      </div>
      <Outlet />
    </>
  );
}
