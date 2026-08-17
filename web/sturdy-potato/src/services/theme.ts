const THEME_KEY = "theme";

export const THEMES = [
  "potato",
  "potato-dark",
  "potato-mint",
  "potato-night",
] as const;
export type Theme = (typeof THEMES)[number];

export const THEME_LABELS: Record<Theme, string> = {
  potato: "Potato",
  "potato-dark": "Potato Dark",
  "potato-mint": "Mint",
  "potato-night": "Night",
};

const DEFAULT_THEME: Theme = "potato";

function isTheme(value: string | null): value is Theme {
  return value !== null && (THEMES as readonly string[]).includes(value);
}

/** The persisted theme, or the default if none was stored. */
export function getTheme(): Theme {
  const stored = localStorage.getItem(THEME_KEY);
  return isTheme(stored) ? stored : DEFAULT_THEME;
}

/** Apply a theme to the document and persist the choice. */
export function setTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem(THEME_KEY, theme);
}

/** Set the document theme from storage without persisting. Call once on boot. */
export function initTheme(): void {
  document.documentElement.dataset.theme = getTheme();
}
