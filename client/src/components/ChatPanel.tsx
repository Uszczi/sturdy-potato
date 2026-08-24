import { useEffect, useRef, useState } from "react";

import {
  ChatTimeoutError,
  streamChat,
  type ChatEvent,
  type ChatMessage,
} from "../services/chat";

/**
 * A chat assistant backed by the local Ollama model. Each turn replays the whole
 * conversation to the server, which streams back tokens (and notes about any
 * task tools it calls) as Server-Sent Events.
 */
function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [activity, setActivity] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Keep the newest message in view as tokens stream in.
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, activity]);

  async function send() {
    const text = input.trim();
    if (!text || streaming) return;

    // Optimistically show the user's message and an empty assistant bubble that
    // fills in as tokens arrive.
    const history: ChatMessage[] = [
      ...messages,
      { role: "user", content: text },
    ];
    setMessages([...history, { role: "assistant", content: "" }]);
    setInput("");
    setStreaming(true);
    setActivity(null);
    setError(null);

    const onEvent = (event: ChatEvent) => {
      if (event.type === "token") {
        setActivity(null);
        setMessages((current) => {
          const next = [...current];
          const last = next[next.length - 1];
          next[next.length - 1] = {
            ...last,
            content: last.content + event.text,
          };
          return next;
        });
      } else if (event.type === "tool_call") {
        setActivity(`Running ${event.name}…`);
      } else if (event.type === "tool_result") {
        setActivity(null);
      }
    };

    try {
      await streamChat(history, onEvent);
    } catch (failure) {
      setError(
        failure instanceof ChatTimeoutError
          ? "The assistant timed out. Try again, or ask something smaller."
          : "The assistant is unavailable. Is Ollama running?",
      );
      // Drop the empty assistant bubble we added for the failed turn.
      setMessages((current) =>
        current[current.length - 1]?.content === ""
          ? current.slice(0, -1)
          : current,
      );
    } finally {
      setStreaming(false);
      setActivity(null);
    }
  }

  function onKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    // Enter sends; Shift+Enter inserts a newline.
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void send();
    }
  }

  return (
    <section className="container mx-auto flex h-[calc(100vh-6rem)] max-w-5xl flex-col px-4 pb-4 sm:px-6 lg:px-8">
      <header className="pb-4">
        <p className="text-base-content/55 text-xs font-bold tracking-wide uppercase">
          Assistant
        </p>
        <h1 className="text-2xl font-black tracking-tight">Chat</h1>
      </header>

      <div
        ref={scrollRef}
        className="border-base-300 bg-base-200/40 rounded-box min-h-0 flex-1 overflow-y-auto border p-4"
      >
        {messages.length === 0 ? (
          <p className="text-base-content/50 grid h-full place-items-center text-sm">
            Ask about your tasks — e.g. “What’s in my inbox?” or “Add a task to
            call the dentist.”
          </p>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`chat ${message.role === "user" ? "chat-end" : "chat-start"}`}
            >
              <div
                className={`chat-bubble ${message.role === "user" ? "chat-bubble-primary" : ""} whitespace-pre-wrap`}
              >
                {message.content || (
                  <span className="loading loading-dots loading-sm" />
                )}
              </div>
            </div>
          ))
        )}

        {activity && (
          <p className="text-base-content/60 mt-1 flex items-center gap-2 text-xs">
            <span className="loading loading-spinner loading-xs" />
            {activity}
          </p>
        )}
      </div>

      {error && (
        <div role="alert" className="alert alert-error mt-3">
          <span>{error}</span>
        </div>
      )}

      <div className="mt-3 flex items-end gap-2">
        <textarea
          className="textarea flex-1 resize-none"
          rows={2}
          placeholder="Message the assistant…"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={onKeyDown}
          disabled={streaming}
        />
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => void send()}
          disabled={streaming || !input.trim()}
        >
          {streaming ? (
            <span className="loading loading-spinner loading-sm" />
          ) : (
            "Send"
          )}
        </button>
      </div>
    </section>
  );
}

export default ChatPanel;
