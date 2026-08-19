/**
 * The preset accent colours a project can wear. Stored on the project as a
 * lower-case "#rrggbb" hex string; a null colour falls back to the theme's
 * primary colour in the UI.
 */
export const PROJECT_COLORS: readonly { name: string; value: string }[] = [
  { name: "Rose", value: "#f43f5e" },
  { name: "Orange", value: "#f97316" },
  { name: "Amber", value: "#f59e0b" },
  { name: "Emerald", value: "#10b981" },
  { name: "Teal", value: "#14b8a6" },
  { name: "Sky", value: "#0ea5e9" },
  { name: "Indigo", value: "#6366f1" },
  { name: "Violet", value: "#8b5cf6" },
];

/** Human label for a stored colour, for accessible descriptions. */
export function colorName(color: string | null | undefined): string {
  if (!color) return "Default";
  const match = PROJECT_COLORS.find(
    (option) => option.value === color.toLowerCase(),
  );
  return match ? match.name : "Custom";
}
