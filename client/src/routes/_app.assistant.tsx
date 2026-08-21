import { createFileRoute } from "@tanstack/react-router";

import ChatPanel from "../components/ChatPanel";

export const Route = createFileRoute("/_app/assistant")({
  component: ChatPanel,
});
