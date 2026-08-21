import { useState } from "react";
import {
  getTheme,
  setTheme,
  THEMES,
  THEME_LABELS,
  type Theme,
} from "../services/theme";

type ThemeToggleProps = {
  /** Renders only the theme choices, for use inside another surface. */
  embedded?: boolean;
};

function ThemeToggle({ embedded = false }: ThemeToggleProps) {
  const [current, setCurrent] = useState<Theme>(getTheme);

  function select(theme: Theme) {
    setTheme(theme);
    setCurrent(theme);
    // Close the dropdown by dropping focus.
    (document.activeElement as HTMLElement | null)?.blur();
  }

  const choices = (
    <ul
      className={
        embedded
          ? "menu w-full gap-1 p-0"
          : "dropdown-content menu rounded-box bg-base-200 z-50 mt-2 w-40 p-2 shadow-xl"
      }
    >
      {THEMES.map((theme) => (
        <li key={theme}>
          <button
            type="button"
            className={theme === current ? "menu-active" : undefined}
            onClick={() => select(theme)}
          >
            <span
              data-theme={theme}
              className="border-base-content/20 bg-primary inline-block size-4 rounded-full border"
            />
            {THEME_LABELS[theme]}
          </button>
        </li>
      ))}
    </ul>
  );

  if (embedded) return choices;

  return (
    <div className="dropdown dropdown-end">
      <div
        tabIndex={0}
        role="button"
        className="btn btn-circle btn-ghost"
        aria-label="Select theme"
      >
        <svg
          className="size-5 fill-current"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
        >
          <path d="M12 2a10 10 0 0 0 0 20 2.5 2.5 0 0 0 2.5-2.5 2.45 2.45 0 0 0-.6-1.6 1 1 0 0 1 .76-1.65H16a6 6 0 0 0 6-6c0-4.96-4.49-9-10-9Zm-5.5 10a1.5 1.5 0 1 1 1.5-1.5A1.5 1.5 0 0 1 6.5 12Zm3-4A1.5 1.5 0 1 1 11 6.5 1.5 1.5 0 0 1 9.5 8Zm5 0A1.5 1.5 0 1 1 16 6.5 1.5 1.5 0 0 1 14.5 8Zm3 4a1.5 1.5 0 1 1 1.5-1.5 1.5 1.5 0 0 1-1.5 1.5Z" />
        </svg>
      </div>

      {choices}
    </div>
  );
}

export default ThemeToggle;
