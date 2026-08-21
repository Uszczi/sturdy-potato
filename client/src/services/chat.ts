/**
 * Client for the streaming chat endpoint (`POST /api/workspaces/{id}/chat/`).
 *
 * The generated OpenAPI client can't consume Server-Sent Events, so this talks
 * to the endpoint with a hand-rolled `fetch` + stream reader. Auth mirrors the
 * generated client: the JWT stashed in localStorage under "access".
 */

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

// The chat route is nested under /workspaces/{id}, like the task routes. Until
// the client threads a chosen workspace everywhere, use the caller's first
// (personal) workspace. Cached so we resolve it once per session.
let workspaceIdCache: number | null = null;

export async function getWorkspaceId(): Promise<number> {
  if (workspaceIdCache !== null) return workspaceIdCache;
  const response = await fetch("/api/workspaces/", { headers: authHeader() });
  if (!response.ok) {
    throw new Error(`Could not load workspace (${response.status})`);
  }
  const workspaces: Array<{ id: number }> = await response.json();
  if (workspaces.length === 0) throw new Error("No workspace available.");
  workspaceIdCache = workspaces[0].id;
  return workspaceIdCache;
}

/**
 * Stream one assistant turn. Sends the whole conversation and calls `onEvent`
 * for each server-sent event until the stream closes. Pass an `AbortSignal` to
 * cancel an in-flight turn.
 */
export async function streamChat(
  messages: ChatMessage[],
  onEvent: (event: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const workspaceId = await getWorkspaceId();
  const response = await fetch(`/api/workspaces/${workspaceId}/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      ...authHeader(),
    },
    body: JSON.stringify({ messages }),
    signal,
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
    buffer += decoder.decode(value, { stream: true });
    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const event = parseSseData(buffer.slice(0, boundary));
      if (event) onEvent(event);
      buffer = buffer.slice(boundary + 2);
      boundary = buffer.indexOf("\n\n");
    }
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
