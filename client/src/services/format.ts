/**
 * Date-only values from the API (`dueDate`) arrive as UTC midnight, so we format
 * them in UTC to avoid a local-timezone off-by-one. Timestamps (`createdAt`,
 * `updatedAt`) are full instants and format in local time.
 */

/** Local `YYYY-MM-DD` key for a date, used to bucket tasks by day. */
export function dayKey(date: Date): string {
  const year = date.getUTCFullYear();
  const month = String(date.getUTCMonth() + 1).padStart(2, "0");
  const day = String(date.getUTCDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/** Today's `YYYY-MM-DD` in the viewer's local timezone. */
export function todayKey(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/** A due date as e.g. "Aug 17" (UTC). */
export function formatDueShort(date: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(date);
}

/** A due date as e.g. "Aug 17, 2026" (UTC). */
export function formatDueLong(date: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  }).format(date);
}

/** A timestamp as e.g. "Aug 17, 2026, 3:04 PM" (local). */
export function formatTimestamp(date: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

/** The long date shown in the overview header, e.g. "Monday, August 17". */
export function formatToday(date: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  }).format(date);
}
