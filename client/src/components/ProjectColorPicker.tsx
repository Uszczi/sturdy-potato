import { useRef } from "react";
import { PROJECT_COLORS, colorName } from "../services/projectColors";

type ProjectColorPickerProps = {
  /** The current colour, or null/undefined for the theme default. */
  value: string | null | undefined;
  /** Called with the chosen hex string, or null to reset to the default. */
  onSelect: (color: string | null) => void;
  /** Accessible label for the trigger (e.g. the project name). */
  label: string;
};

/**
 * A swatch button that opens a small palette of preset project colours. Picking
 * a swatch (or "Default") calls `onSelect` and closes the dropdown.
 */
function ProjectColorPicker({ value, onSelect, label }: ProjectColorPickerProps) {
  const detailsRef = useRef<HTMLDetailsElement>(null);

  function choose(color: string | null) {
    onSelect(color);
    if (detailsRef.current) detailsRef.current.open = false;
  }

  return (
    <details ref={detailsRef} className="dropdown">
      <summary
        className="grid size-6 cursor-pointer place-items-center rounded-full ring-1 ring-base-300 transition hover:ring-base-content/30 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
        aria-label={`Color for ${label}: ${colorName(value)}`}
      >
        <ProjectDot color={value} className="size-3" />
      </summary>
      <div className="dropdown-content z-10 mt-2 rounded-box border border-base-300 bg-base-100 p-3 shadow-lg">
        <p className="mb-2 text-xs font-bold tracking-wider text-base-content/50 uppercase">
          Color
        </p>
        <div className="grid grid-cols-4 gap-2">
          {PROJECT_COLORS.map((option) => {
            const selected = value?.toLowerCase() === option.value;
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => choose(option.value)}
                aria-label={option.name}
                aria-pressed={selected}
                className={`grid size-7 place-items-center rounded-full transition ${
                  selected
                    ? "ring-2 ring-base-content ring-offset-2 ring-offset-base-100"
                    : "hover:scale-110"
                }`}
                style={{ backgroundColor: option.value }}
              >
                {selected && (
                  <svg
                    aria-hidden="true"
                    className="size-4 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth="3"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="m5 12 4 4L19 6"
                    />
                  </svg>
                )}
              </button>
            );
          })}
        </div>
        <button
          type="button"
          onClick={() => choose(null)}
          className="btn mt-3 w-full justify-start btn-ghost btn-sm"
        >
          <ProjectDot color={null} className="size-3" />
          Default
        </button>
      </div>
    </details>
  );
}

/**
 * The coloured dot that marks a project. Uses the project's colour when set and
 * falls back to the theme's primary colour otherwise.
 */
export function ProjectDot({
  color,
  className = "size-2.5",
}: {
  color: string | null | undefined;
  className?: string;
}) {
  return (
    <span
      className={`${className} shrink-0 rounded-full ${color ? "" : "bg-primary/75"}`}
      style={color ? { backgroundColor: color } : undefined}
      aria-hidden="true"
    />
  );
}

export default ProjectColorPicker;
