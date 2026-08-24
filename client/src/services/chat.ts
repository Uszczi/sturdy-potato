/**
 * Client for the streaming chat endpoint (`POST /api/chat/`).
 *
 * The generated OpenAPI client can't consume Server-Sent Events, so this talks
 * to the endpoint with a hand-rolled `fetch` + stream reader. Auth mirrors the
 * generated client: the JWT stashed in localStorage under "access".
 */

/**
 * How long a turn may stay silent before the client gives up.
 *
 * The timer is reset by every chunk that arrives, so this caps *silence*, not
 * the length of a turn: a long answer streams indefinitely, while a wedged
 * Ollama or MCP server eventually fails instead of spinning forever.
 *
 * Deliberately long: the quiet stretches are real — a cold model load, or a
 * tool round waiting on the MCP server — and a false timeout throws away a turn
 * that was still coming. Raising it further is fine up to 2**31-1 ms (~24.8
 * days), above which `setTimeout` overflows its signed 32-bit delay and fires
 * immediately.
 */
export const CHAT_IDLE_TIMEOUT_MS = 30 * 60 * 1000;

/** Raised when a turn went `CHAT_IDLE_TIMEOUT_MS` without any data. */
export class ChatTimeoutError extends Error {
  constructor() {
    super(
      `The assistant sent nothing for ${CHAT_IDLE_TIMEOUT_MS / 60_000} minutes.`,
    );
    this.name = "ChatTimeoutError";
  }
}

/** One turn of the conversation the assistant sees. */
export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

/** The events the server streams back over the turn. */
export type ChatEvent =
  | { type: "token"; text: string }
  | { type: "tool_call"; name: string; arguments: Record<string, unknown> }
  | { type: "tool_result"; name: string }
  | { type: "done"; note?: string };

function authHeader(): Record<string, string> {
  const token = localStorage.getItem("access");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/**
 * Stream one assistant turn. Sends the whole conversation and calls `onEvent`
 * for each server-sent event until the stream closes. Pass an `AbortSignal` to
 * cancel an in-flight turn; a turn that goes quiet for `CHAT_IDLE_TIMEOUT_MS`
 * aborts itself and throws `ChatTimeoutError`.
 */
export async function streamChat(
  messages: ChatMessage[],
  onEvent: (event: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  // One controller drives both cancellation paths — the caller's signal and the
  // idle timer — because `fetch` takes a single signal and aborting it is also
  // what unblocks a `reader.read()` that is waiting on a dead stream.
  const controller = new AbortController();
  const cancel = () => controller.abort();
  signal?.addEventListener("abort", cancel);
  let timedOut = false;
  let idleTimer: ReturnType<typeof setTimeout> | undefined;
  const resetIdleTimer = () => {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, CHAT_IDLE_TIMEOUT_MS);
  };

  try {
    resetIdleTimer();
    const response = await fetch("/api/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
        ...authHeader(),
      },
      body: JSON.stringify({ messages }),
      signal: controller.signal,
    });
    if (!response.ok || !response.body) {
      throw new Error(`Chat request failed (${response.status})`);
    }

    // Parse the SSE stream: events are separated by a blank line; we read the
    // `data:` payload of each and JSON-parse it. Comment lines (":") are ignored.
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      resetIdleTimer();
      buffer += decoder.decode(value, { stream: true });
      let boundary = buffer.indexOf("\n\n");
      while (boundary !== -1) {
        const event = parseSseData(buffer.slice(0, boundary));
        if (event) onEvent(event);
        buffer = buffer.slice(boundary + 2);
        boundary = buffer.indexOf("\n\n");
      }
    }
  } catch (error) {
    // The abort surfaces as a generic AbortError, so our own flag is what tells
    // "the model went silent" apart from "the caller cancelled".
    if (timedOut) throw new ChatTimeoutError();
    throw error;
  } finally {
    clearTimeout(idleTimer);
    signal?.removeEventListener("abort", cancel);
  }
}

/** Extract and JSON-parse the `data:` payload from one SSE event block. */
function parseSseData(block: string): ChatEvent | null {
  const data = block
    .split("\n")
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trim())
    .join("\n");
  if (!data) return null;
  try {
    return JSON.parse(data) as ChatEvent;
  } catch {
    return null;
  }
}
