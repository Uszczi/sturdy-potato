import { Configuration, ApiApi } from "../api-client";

// The dev server (`just run`, uvicorn) binds 127.0.0.1 only (IPv4). Using the
// literal 127.0.0.1 avoids the browser resolving "localhost" to ::1 (IPv6),
// where nothing listens — that failed connection surfaces as a misleading
// "CORS request did not succeed" with a null status code.
const BASE_PATH = "http://127.0.0.1:8000";

// The generated client reads `accessToken` lazily on every request, so we point
// it at localStorage. After logging in we stash the JWT there and every
// subsequent call sends `Authorization: Bearer <token>` automatically.
export const api = new ApiApi(
  new Configuration({
    basePath: BASE_PATH,
    accessToken: () => localStorage.getItem("access") ?? "",
  }),
);
