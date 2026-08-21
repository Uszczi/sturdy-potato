import {
  Outlet,
  createRootRouteWithContext,
  useLocation,
} from "@tanstack/react-router";
import ThemeToggle from "../components/ThemeToggle";

export type RouterContext = {
  isAuthenticated: () => boolean;
};

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

function RootLayout() {
  const { pathname } = useLocation();
  const showThemeToggle = pathname === "/login" || pathname === "/register";

  return (
    <>
      {showThemeToggle && (
        <div className="fixed top-4 right-4 z-50">
          <ThemeToggle />
        </div>
      )}
      <Outlet />
    </>
  );
}
