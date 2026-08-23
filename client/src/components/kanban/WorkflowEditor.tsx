import { useEffect, useRef, useState } from "react";
import type { StatusInput } from "@api-client";

import { useAppStore } from "@/stores/app-store";

// Mirrors the server's own ceiling (use_cases/workflow.py). Enforced here only
// so "Add column" stops before a save that the server would reject.
const MAX_STATUSES = 50;

/**
 * Turn a label into a status key. Keys are what task rows store, so they are
 * generated once when a status is created and never change again — renaming the
 * label afterwards leaves every task where it is.
 */
function keyFor(label: string, taken: Set<string>): string {
  const base =
    label
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 20) || "status";
  if (!taken.has(base)) return base;
  for (let suffix = 2; ; suffix++) {
    const candidate = `${base.slice(0, 18)}-${suffix}`;
    if (!taken.has(candidate)) return candidate;
  }
}

/**
 * Edit one board's columns: add, rename, reorder and remove statuses.
 *
 * Everything is staged locally and sent as one complete list, because the rules
 * a workflow has to satisfy (exactly one initial status, at least one terminal)
 * only hold for a finished list — applying the steps one at a time would have to
 * pass through states that break them.
 */
export default function WorkflowEditor({
  projectId,
  boardName,
}: {
  projectId: number | null;
  boardName: string;
}) {
  const saved = useAppStore((state) => state.getWorkflow(projectId));
  const saveWorkflow = useAppStore((state) => state.saveWorkflow);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [draft, setDraft] = useState<StatusInput[]>([]);
  // Where each removed status's tasks go, keyed by the removed status's key.
  const [reassign, setReassign] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Start every editing session from what the server currently holds.
  function open() {
    setDraft(saved.map((status) => ({ ...status })));
    setReassign({});
    setError(null);
    dialogRef.current?.showModal();
  }

  const draftKeys = new Set(draft.map((status) => status.key));
  const removed = saved.filter((status) => !draftKeys.has(status.key));

  // Drop targets that no longer make sense: a status re-added after being
  // removed strands its pending target, and a column chosen as a target can
  // itself be removed afterwards. Either way the select falls back to "Choose a
  // column" so the gap is named here rather than as a server rejection.
  useEffect(() => {
    setReassign((current) => {
      const stale = Object.keys(current).filter(
        (key) =>
          !removed.some((status) => status.key === key) ||
          !draftKeys.has(current[key]),
      );
      if (stale.length === 0) return current;
      const next = { ...current };
      for (const key of stale) delete next[key];
      return next;
    });
    // `removed` and `draftKeys` are both derived from draft.
  }, [draft]); // eslint-disable-line react-hooks/exhaustive-deps

  function edit(index: number, changes: Partial<StatusInput>) {
    setDraft((current) =>
      current.map((status, at) =>
        at === index ? { ...status, ...changes } : status,
      ),
    );
  }

  function move(index: number, by: number) {
    const to = index + by;
    if (to < 0 || to >= draft.length) return;
    setDraft((current) => {
      const next = [...current];
      const [lifted] = next.splice(index, 1);
      next.splice(to, 0, lifted);
      return next;
    });
  }

  function add() {
    setDraft((current) => [
      ...current,
      {
        key: keyFor("status", new Set(current.map((s) => s.key))),
        label: "New status",
        isInitial: false,
        isTerminal: false,
      },
    ]);
  }

  /** Exactly one status is initial, so choosing one clears the others. */
  function chooseInitial(index: number) {
    setDraft((current) =>
      current.map((status, at) => ({ ...status, isInitial: at === index })),
    );
  }

  async function save() {
    const missing = removed.filter((status) => !reassign[status.key]);
    if (missing.length > 0) {
      setError(
        `Choose where the tasks in ${missing
          .map((status) => status.label)
          .join(", ")} should go.`,
      );
      return;
    }
    setSaving(true);
    setError(null);
    const ok = await saveWorkflow(projectId, { statuses: draft, reassign });
    setSaving(false);
    if (ok) dialogRef.current?.close();
    else setError("That workflow was rejected. Check the columns and retry.");
  }

  return (
    <>
      <button type="button" className="btn btn-sm btn-block" onClick={open}>
        Edit columns
      </button>

      <dialog ref={dialogRef} className="modal">
        <div className="modal-box max-w-2xl">
          <h3 className="text-lg font-bold">Columns for {boardName}</h3>
          <p className="text-base-content/60 mt-1 text-sm">
            Cards start in the initial column and count as finished in any
            terminal one.
          </p>

          <ul className="mt-4 flex flex-col gap-2">
            {draft.map((status, index) => (
              <li
                key={status.key}
                className="border-base-300 rounded-box flex flex-wrap items-center gap-2 border p-2"
              >
                <div className="join">
                  <button
                    type="button"
                    className="btn btn-xs join-item"
                    onClick={() => move(index, -1)}
                    disabled={index === 0}
                    aria-label={`Move ${status.label} earlier`}
                  >
                    ↑
                  </button>
                  <button
                    type="button"
                    className="btn btn-xs join-item"
                    onClick={() => move(index, 1)}
                    disabled={index === draft.length - 1}
                    aria-label={`Move ${status.label} later`}
                  >
                    ↓
                  </button>
                </div>

                <input
                  type="text"
                  className="input input-sm flex-1"
                  value={status.label}
                  aria-label="Column name"
                  onChange={(event) => {
                    const label = event.target.value;
                    // A status the server has never seen can still take a key
                    // derived from its name; a saved one is stuck with its own.
                    const isNew = !saved.some((s) => s.key === status.key);
                    const taken = new Set(
                      draft
                        .filter((_, at) => at !== index)
                        .map((s) => s.key)
                        .concat(saved.map((s) => s.key)),
                    );
                    edit(index, {
                      label,
                      ...(isNew ? { key: keyFor(label, taken) } : null),
                    });
                  }}
                />

                <label className="label gap-1 text-xs">
                  <input
                    type="radio"
                    name="initial-status"
                    className="radio radio-xs"
                    checked={status.isInitial}
                    onChange={() => chooseInitial(index)}
                  />
                  Start
                </label>

                <label className="label gap-1 text-xs">
                  <input
                    type="checkbox"
                    className="checkbox checkbox-xs"
                    checked={status.isTerminal}
                    onChange={(event) =>
                      edit(index, { isTerminal: event.target.checked })
                    }
                  />
                  Done
                </label>

                <button
                  type="button"
                  className="btn btn-xs btn-ghost"
                  onClick={() =>
                    setDraft((current) =>
                      current.filter((_, at) => at !== index),
                    )
                  }
                  disabled={draft.length <= 2}
                  aria-label={`Remove ${status.label}`}
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>

          <button
            type="button"
            className="btn btn-sm mt-3"
            onClick={add}
            disabled={draft.length >= MAX_STATUSES}
          >
            Add column
          </button>

          {removed.length > 0 && (
            <fieldset className="fieldset mt-4">
              <legend className="fieldset-legend">Move remaining cards</legend>
              {removed.map((status) => (
                <label
                  key={status.key}
                  className="flex items-center gap-2 text-sm"
                >
                  <span className="min-w-24">{status.label} →</span>
                  <select
                    className="select select-sm"
                    value={reassign[status.key] ?? ""}
                    aria-label={`Move cards from ${status.label} to`}
                    onChange={(event) =>
                      setReassign((current) => ({
                        ...current,
                        [status.key]: event.target.value,
                      }))
                    }
                  >
                    <option value="" disabled>
                      Choose a column
                    </option>
                    {draft.map((target) => (
                      <option key={target.key} value={target.key}>
                        {target.label}
                      </option>
                    ))}
                  </select>
                </label>
              ))}
            </fieldset>
          )}

          {error !== null && (
            <div role="alert" className="alert alert-error mt-4">
              <span>{error}</span>
            </div>
          )}

          <div className="modal-action">
            <form method="dialog">
              <button className="btn btn-ghost">Cancel</button>
            </form>
            <button
              type="button"
              className="btn btn-primary"
              onClick={save}
              disabled={saving}
            >
              Save
            </button>
          </div>
        </div>
        <form method="dialog" className="modal-backdrop">
          <button>close</button>
        </form>
      </dialog>
    </>
  );
}
